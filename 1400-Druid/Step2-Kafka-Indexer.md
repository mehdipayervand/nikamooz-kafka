**Hint :**

you can use official `Druid` docker image to build your own customized version. please refer to :

[druid/distribution/docker at master · apache/druid (github.com)](https://github.com/apache/druid/tree/master/distribution/docker)

#### 1- Start a Kafka Cluster :

- go to `Docker` folder and run the following command to setup a simple Kafka cluster :

  - `docker-compose up -d`
  - **Kafka HQ UI** : `http://localhost:8000`
  
  - this file will start a `postgres` node . 

####  2- Start Druid 

- in `WSL`, go into druid installation folder,  go to `conf/druid/single-server/micro-quickstart/middleManager`

  - `nano runtime.properties`

    ```bash
    # Number of tasks per middleManager
    druid.worker.capacity=5
    ```

- in `WSL`, go into druid folder and run :

  - `./ bin/start-micro-quickstart`

#### 3- Generate Some Fake Events in Kafka

- open a `console terminal` (`WSL` or `Powershell` or ...) and go to `Codes` folder - in `Section 21`
- Create a `venv` and activate it. (in `Codes` directory)
  - `python -m venv .venv`
  - ` .\.venv\Scripts\activate`

- install requirements 
  - `pip install -r requirements.txt`
- run `python user_event_producer.py`
  - data is streamed into `events_topic` topics.

#### 4- Load Kafka data into Druid

- click load data 

- select apache `kafka` 

- follow the instructions in Druid Official Docs for ingesting `kafka` topics.
  - create a `user-events` `datasource`. (segment granularity : `Daily`)
    - Transform value to 3 levels : **High/Medium/Low** 
    - Use `if` expression :
  
    ```sql
    if (event_value>7000,'High', if (event_value>3000,'Medium','Low'))
    ```
  
    - Check `ingestion` section : supervisors, tasks , available slots , suspend/resume supervisor, open data loader , ....
  
  - create a rollup `datasource`- Monthly/Stats - Per Page (`datasource` name : `user_events_page_monthly_rollups`)
  
    - use transform section to extract the main page
  
      - add a new column `domain` : first part of `page` column (`splitted by /`)
  
      ```sql
      substring(page,0,strpos(page,'/'))
      ```
  
    - Wrong way : use ` timestamp_extract( __time, 'Month', 'Asia/Tehran' ) `  as Month Column
  
    - Correct Way : set `Query granularity` to `Month`
  
  - create a rollup `datasource`  - Product Daily Rollup / User Stats Sketches.  (`datasource` name : `product_daily_stats`)
  
    - add `count, min_valu , max_value` metric fields.
  
    - drop `user_name`, `event_id` , `page`
  
    - add thetaSketch for `user_name` and name it `user_stats`
  
    - set `Query granularity` to daily.
  
    - Query the user_stats : 
  
      ```sql
    SELECT  __time,  event_type,count_events,product_id, APPROX_COUNT_DISTINCT_DS_THETA(user_stats) as UserStats
      FROM product_daily_stats
      GROUP BY __time,event_type,count_events,product_id
      ```
    
      
  

#### 5 - Reindex `user-events`

- Reindex `user-events`
  - change segment granularity into `Monthly`
  - filter out some rows. for example : 
  
   ```json
    {
      "type": "and",
      "fields": [
        {
          "type": "or",
          "fields": [
            {
              "type": "selector",
              "dimension": "event_type",
              "value": "buy"
            },
            {
              "type": "selector",
              "dimension": "event_type",
              "value": "click"
            }
          ]
        },
        {
          "field": {
            "type": "selector",
            "dimension": "user_name",
            "value": "clong"
          },
          "type": "not"
        }
      ]
    }
   ```
  
  - compact `user_events` 
  
    - `submit` this task : 
  
    ```json
    {
      "type": "compact",
      "dataSource": "user-events",
      "interval": "2021-09-01/2021-12-29",
      "tuningConfig" : {
        "type" : "index_parallel",
        "maxRowsPerSegment" : 5000000,
        "maxRowsInMemory" : 25000
      }
    }
    ```
  
    

#### 6 - add Product Lookup   from Postgres

- in `WSL`, go into druid installation folder,  go to `/conf/druid/single-server/micro-quickstart/_common`

  - `nano common.runtime.properties`

    ```bash
    
    # If you specify `druid.extensions.loadList=[]`, Druid won't load any extension from file system.
    # If you don't specify `druid.extensions.loadList`, Druid will load all the extensions under root extension directory.
    # More info: https://druid.apache.org/docs/latest/operations/including-extensions.html
    druid.extensions.loadList=["druid-hdfs-storage", "druid-kafka-indexing-service", "druid-datasketches", "druid-lookups-cached-global"]
    ```

  - copy `postgres` driver jar from `extensions` directory to `lib` directory : 

    ```bash
    $ cp extensions/postgresql-metadata-storage/postgresql-42.2.14.jar lib/
    ```

  - restart the `Druid`

- create a sample product table in Postgres ( check out the `docker-compose` file for user/pass info, open `DBeaver` and create a `products` table with 2 fields  : `id` / `name` )

- connect druid lookup to this table

  - name : `products`
  - settings :

  ```json
  {
    "type": "cachedNamespace",
    "extractionNamespace": {
      "type": "jdbc",
      "pollPeriod": "PT1M",
      "connectorConfig": {
        "connectURI": "jdbc:postgresql://localhost:5432/lookups",
        "user": "druid",
        "password": "druid123"
      },
      "table": "products",
      "keyColumn": "id",
      "valueColumn": "name"
    }
  }
  ```

  - Wait some time to lookup data to be fully loaded.

- query `user_event` using lookup function

```sql
SELECT  LOOKUP(product_id , 'products') as product_name, count(*) as product_count
FROM events
GROUP BY product_id
order by 2 DESC
```



