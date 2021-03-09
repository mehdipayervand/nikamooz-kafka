#### Prerequisites

- docker (`Docker Desktop` for windows)
- linux terminal (`WSL` in windows  with one linux distribution installed)
- `dbeaver` free universal database tools



##### Webinar References 

- dd
-  



#### Run Basic Docker Images

###### Postgres

- basic config

```bash
docker run -d --name postgres -p 5432:5432 -e POSTGRES_USER=start_data_engineer \
-e POSTGRES_PASSWORD=password debezium/postgres:1
```

- replication settings



###### Zookeeper

- basic config 







