## [https://gitlab.com/nikamooz_bigdata/webinars](https://gitlab.com/nikamooz_bigdata/webinars)

#### Prerequisites

- docker (`Docker Desktop` for windows)
- linux terminal (`WSL` in windows  with one linux distribution installed)
- `dbeaver` free universal database tools



##### Webinar References 

- [Tutorial :: Debezium Documentation - MySQL Version](https://debezium.io/documentation/reference/tutorial.html)
-  [Change Data Capture Using Debezium Kafka and Pg · Start Data Engineering](https://www.startdataengineering.com/post/change-data-capture-using-debezium-kafka-and-pg/)



#### Run Basic Docker Images

###### Postgres

- basic config

```bash
docker run -d --name postgres -p 5432:5432 -e POSTGRES_USER=start_data_engineer \
-e POSTGRES_PASSWORD=password debezium/postgres:12
```

- replication settings

```bash
$ docker exec -ti postgres /bin/bash

$ cat /var/lib/postgresql/data/postgresql.conf


```

- Use `DBeaver `

  ```sql
use database start_data_engineer;
  CREATE SCHEMA bank;
  SET search_path TO bank,public;
  CREATE TABLE bank.holding (
      holding_id int,
      user_id int,
      holding_stock varchar(8),
      holding_quantity int,
      datetime_created timestamp,
      datetime_updated timestamp,
      primary key(holding_id)
  );
  ALTER TABLE bank.holding replica identity FULL;
  insert into bank.holding values (1000, 1, 'VFIAX', 10, now(), now());
  ```

 The above is standard sql, with the addition of `replica identity`. 

This field has the option of being set as one of `DEFAULT, NOTHING, FULL and INDEX` which determines the amount of detailed information written to the WAL. We choose FULL to get all the before and after data for CRUD change events in our WAL, the `INDEX` option is the same as full but it also includes changes made to indexes in WAL which we do not require for our project’s objective. We also insert a row into the holding table

###### Zookeeper /Kafka

- basic config 

```bash
docker run -d --name zookeeper -p 2181:2181 -p 2888:2888 -p 3888:3888 debezium/zookeeper:1.1
docker run -d --name kafka -p 9092:9092 --link zookeeper:zookeeper debezium/kafka:1.1
```



###### Debezium

- basic confi

  ```bash
  docker run -d --name connect -p 8083:8083 --link kafka:kafka \
  --link postgres:postgres -e BOOTSTRAP_SERVERS=kafka:9092 \
  -e GROUP_ID=sde_group -e CONFIG_STORAGE_TOPIC=sde_storage_topic \
  -e OFFSET_STORAGE_TOPIC=sde_offset_topic debezium/connect:1.1
  ```



##### Lets Start

- check connectors 

```bash
$ curl -H "Accept:application/json" localhost:8083/connectors/
[]

$ curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '{"name": "sde-connector", "config": {"connector.class": "io.debezium.connector.postgresql.PostgresConnector", "database.hostname": "postgres", "database.port": "5432", "database.user": "start_data_engineer", "database.password": "password", "database.dbname" : "start_data_engineer", "database.server.name": "bankserver1", "table.whitelist": "bank.holding"}}'


```



- What We Done : 

```json
{
  "name": "sde-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "start_data_engineer",
    "database.password": "password",
    "database.dbname": "start_data_engineer",
    "database.server.name": "bankserver1",
    "table.whitelist": "bank.holding"
  }
}

```



- check the connectors :

```bash
$ curl -H "Accept:application/json" localhost:8083/connectors/
```



###### Consumer

```bash
docker run -it --rm --name consumer --link zookeeper:zookeeper --link kafka:kafka debezium/kafka:1.1 watch-topic -a bankserver1.bank.holding --max-messages 1 | grep '^{' | jq
```



##### a Python Parser

- write a file in home directory named `stream.py`

  ```bash
  $ cd 
  $ nano stream.py
  
  
  ```

  ```python
  #!/usr/bin/python3 -u
  # Note: the -u denotes unbuffered (i.e output straing to stdout without buffering data and then writing to stdout)
  
  import json
  import os
  import sys
  from datetime import datetime
  
  FIELDS_TO_PARSE = ['holding_stock', 'holding_quantity']
  
  
  def parse_create(payload_after, op_type):
      current_ts = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
      out_tuples = []
      for field_to_parse in FIELDS_TO_PARSE:
          out_tuples.append(
              (
                  payload_after.get('holding_id'),
                  payload_after.get('user_id'),
                  field_to_parse,
                  None,
                  payload_after.get(field_to_parse),
                  payload_after.get('datetime_created'),
                  None,
                  None,
                  current_ts,
                  op_type
              )
          )
  
      return out_tuples
  
  
  def parse_delete(payload_before, ts_ms, op_type):
      current_ts = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
      out_tuples = []
      for field_to_parse in FIELDS_TO_PARSE:
          out_tuples.append(
              (
                  payload_before.get('holding_id'),
                  payload_before.get('user_id'),
                  field_to_parse,
                  payload_before.get(field_to_parse),
                  None,
                  None,
                  ts_ms,
                  current_ts,
                  op_type
              )
          )
  
      return out_tuples
  
  
  def parse_update(payload, op_type):
      current_ts = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
      out_tuples = []
      for field_to_parse in FIELDS_TO_PARSE:
          out_tuples.append(
              (
                  payload.get('after', {}).get('holding_id'),
                  payload.get('after', {}).get('user_id'),
                  field_to_parse,
                  payload.get('before', {}).get(field_to_parse),
                  payload.get('after', {}).get(field_to_parse),
                  None,
                  payload.get('ts_ms'),
                  None,
                  current_ts,
                  op_type
              )
          )
  
      return out_tuples
  
  
  def parse_payload(input_raw_json):
      input_json = json.loads(input_raw_json)
      op_type = input_json.get('payload', {}).get('op')
      if op_type == 'c':
          return parse_create(
              input_json.get('payload', {}).get('after', {}),
              op_type
          )
      elif op_type == 'd':
          return parse_delete(
              input_json.get('payload', {}).get('before', {}),
              input_json.get('payload', {}).get('ts_ms', None),
              op_type
          )
      elif op_type == 'u':
          return parse_update(
              input_json.get('payload', {}),
              op_type
          )
      # no need to log read events
      return []
  
  
  for line in sys.stdin:
      # 1. reads line from unix pipe, assume only valid json come through
      # 2. parse the payload into a format we can use
      # 3. prints out the formatted data as a string to stdout
      # 4. the string is of format
      #    holding_id, user_id, change_field, old_value, new_value, datetime_created, datetime_updated, datetime_deleted, datetime_inserted
      data = parse_payload(line)
      for log in data:
          log_str = ','.join([str(elt) for elt in log])
          print(log_str, flush=True)
  ```

- make `stream.py` executable

  ```bash
  $ chmod +x stream.py
  ```
  
  
  
- run the consumer 

  ```bash
  $ docker run -it --rm --name consumer --link zookeeper:zookeeper \
  --link kafka:kafka debezium/kafka:1.1 watch-topic \
  -a bankserver1.bank.holding | grep --line-buffered '^{' \
  | ./stream.py > ./holding_pivot.txt
  ```
  
  
  
  



