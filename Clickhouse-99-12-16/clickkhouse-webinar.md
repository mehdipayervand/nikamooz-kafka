#### Install Clickhouse 

- We used Ubuntu 20 installed in Windows WSL  

- [Installation Guide](https://clickhouse.tech/docs/en/getting-started/install/) :

```bash
  sudo apt-get install apt-transport-https ca-certificates dirmngr
  sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv E0C56BD4
  
  echo "deb https://repo.clickhouse.tech/deb/stable/ main/" | sudo tee \
      /etc/apt/sources.list.d/clickhouse.list
  sudo apt-get update
  
  sudo apt-get install -y clickhouse-server clickhouse-client
  
  sudo service clickhouse-server start
  clickhouse-client
```

#### Create Hourly Table

- use `DBeaver` for working with `Clickhouse` or you can try clickhouse-client

  ```sql
  
  CREATE database analytics;
  
  CREATE TABLE analytics.daily_stats 
  ( 
      id  UInt64  Codec(T64),
      viewed UInt64  Codec(T64),
      clicked UInt64 Codec(T64) ,
      income UInt64 Codec(T64) ,
      date_stamp Date,
      campaign_id UInt32 
  )
  ENGINE = MergeTree()
  PARTITION BY toYYYYMM(date_stamp)
  --By default the primary key is the same as the sorting key
  ORDER BY (date_stamp, campaign_id)
  ;
  
  
  CREATE TABLE analytics.monthly_stats 
  ( 
      viewed UInt64  Codec(T64),
      clicked UInt64 Codec(T64) ,
      income UInt64 Codec(T64) ,
      month_stamp Date,
      campaign_id UInt32 
  )
  ENGINE = SummingMergeTree()
  PARTITION BY toYear(month_stamp)
  ORDER BY (month_stamp, campaign_id)
  ;
  
  
  CREATE MATERIALIZED VIEW analytics.mv_monthly_stats
  TO analytics.monthly_stats AS
  SELECT sum(viewed) as viewed,sum(clicked) as clicked, sum(income)as income, toStartOfMonth(date_stamp) as month_stamp, campaign_id 
  FROM analytics.daily_stats ds
  group by toStartOfMonth(date_stamp), campaign_id
  ; 
  
  
  insert into analytics.daily_stats(id,viewed,clicked,income,date_stamp,campaign_id) 
  values  (1,10,1,1000,'2021-03-06',1001) ,
  		(2,20,2,2000,'2021-03-05',1001) ,
  		(3,30,3,3000,'2021-03-06',1002) ,
  		(4,50,5,3000,'2021-03-05',1002) ,
  		(5,10,1,1000,'2021-04-06',1001) ,
  		(6,20,2,2000,'2021-04-05',1001) ,
  		(7,30,3,3000,'2021-02-06',1002) ,
  		(8,50,5,3000,'2021-02-05',1002) 
  	;
  ```
  
  #### Load CSV Data
  
  ```bash
  $ clickhouse-client --query="INSERT INTO analytics.daily_stats  FORMAT CSV" < daily_stats_0.csv
  $  clickhouse-client --query="INSERT INTO analytics.daily_stats  FORMAT CSV" < daily_stats_1.csv
  $  clickhouse-client --query="INSERT INTO analytics.daily_stats  FORMAT CSV" < daily_stats_2.csv
  ```
  
  ##### check out the result :
  ```sql
  select count(*) 
  from analytics.daily_stats ds ;
  
  select count(*) 
  from analytics.monthly_stats ms  ;
  
  select name, formatReadableSize(sum(data_compressed_bytes)) as compressed, 
  		formatReadableSize(sum(data_uncompressed_bytes)) as uncompressed, 
  		sum(data_compressed_bytes)*100/sum(data_uncompressed_bytes) as compress_ratio  
  from system.columns  
  where table = 'daily_stats' group by name with totals order by sum(data_compressed_bytes);
  
  
  
  select concat(database, '.', table)                         as table,
         formatReadableSize(sum(bytes))                       as size,
         sum(rows)                                            as rows,
         max(modification_time)                               as latest_modification,
         sum(bytes)                                           as bytes_size,
         any(engine)                                          as engine,
         formatReadableSize(sum(primary_key_bytes_in_memory)) as primary_keys_size
  from system.parts
  where active
  group by database, table
  order by bytes_size desc;
  ```
