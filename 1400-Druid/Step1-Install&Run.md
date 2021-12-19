#### Download & Run Druid
- download Druid from https://druid.apache.org/downloads.html
- copy zip file into `apps` folder in `WSL` home directory (`~/home`)
- unzip druid : `tar -xvf apache-druid-0.22.0-bin.tar.gzip`
- verify java version
```bash
$ cp apache-druid-0.22.0-bin.tar.gzip ~/apps
$ tar -xvf apache-druid-0.22.0-bin.tar.gzip
$ cd ~/apache-druid-0.22.0
$ ./bin/verify-java

Druid only officially supports Java 8. Any Java version later than 8 is still experimental. Your current version is: 11.0.11.

If you believe this check is in error or you still want to proceed with Java version other than 8,
you can skip this check using an environment variable:

  export DRUID_SKIP_JAVA_CHECK=1

Otherwise, install Java 8 and try again.

This script searches for Java 8 in 3 locations in the following
order
  * DRUID_JAVA_HOME
  * JAVA_HOME
  * java (installed on PATH)
  
  

```

- run this command 

` export DRUID_SKIP_JAVA_CHECK=1`

Verify Again : `./bin/verify-java`

##### Run Druid - Micro Quick Start 

```bash
$ ./bin/start-micro-quickstart
[Fri May  3 11:40:50 2019] Running command[zk], logging to[/apache-druid-0.22.0/var/sv/zk.log]: bin/run-zk conf
[Fri May  3 11:40:50 2019] Running command[coordinator-overlord], logging to[/apache-druid-0.22.0/var/sv/coordinator-overlord.log]: bin/run-druid coordinator-overlord conf/druid/single-server/micro-quickstart
[Fri May  3 11:40:50 2019] Running command[broker], logging to[/apache-druid-0.22.0/var/sv/broker.log]: bin/run-druid broker conf/druid/single-server/micro-quickstart
[Fri May  3 11:40:50 2019] Running command[router], logging to[/apache-druid-0.22.0/var/sv/router.log]: bin/run-druid router conf/druid/single-server/micro-quickstart
[Fri May  3 11:40:50 2019] Running command[historical], logging to[/apache-druid-0.22.0/var/sv/historical.log]: bin/run-druid historical conf/druid/single-server/micro-quickstart
[Fri May  3 11:40:50 2019] Running command[middleManager], logging to[/apache-druid-0.22.0/var/sv/middleManager.log]: bin/run-druid middleManager conf/druid/single-server/micro-quickstart
```



## Step 3. Open the Druid console

After the Druid services finish startup, open the [Druid console](https://druid.apache.org/docs/latest/operations/druid-console.html) at [http://localhost:8888](http://localhost:8888/).



## Step 4. Load data -Quick Start

The Druid distribution bundles sample data we can use. The sample data located in `quickstart/tutorial/wikiticker-2015-09-12-sampled.json.gz` in the Druid root directory represents Wikipedia page edits for a given day.

1. Click **Load data** from the Druid console header (![Load data](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-00.png)).

2. Select the **Local disk** tile and then click **Connect data**.

   ![Data loader init](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-01.png)

3. Enter the following values:

   - **Base directory**: `quickstart/tutorial/`
   - **File filter**: `wikiticker-2015-09-12-sampled.json.gz`

   ![Data location](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-015.png)

   Entering the base directory and [wildcard file filter](https://commons.apache.org/proper/commons-io/apidocs/org/apache/commons/io/filefilter/WildcardFileFilter.html) separately, as afforded by the UI, allows you to specify multiple files for ingestion at once.

4. Click **Apply**.

   The data loader displays the raw data, giving you a chance to verify that the data appears as expected.

   ![Data loader sample](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-02.png)

   Notice that your position in the sequence of steps to load data, **Connect** in our case, appears at the top of the console, as shown below. You can click other steps to move forward or backward in the sequence at any time.

   ![Load data](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-12.png)

1. Click **Next: Parse data**.

   The data loader tries to determine the parser appropriate for the data format automatically. In this case it identifies the data format as `json`, as shown in the **Input format** field at the bottom right.

   ![Data loader parse data](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-03.png)

   Feel free to select other **Input format** options to get a sense of their configuration settings and how Druid parses other types of data.

2. With the JSON parser selected, click **Next: Parse time**. The **Parse time** settings are where you view and adjust the primary timestamp column for the data.

   ![Data loader parse time](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-04.png)

   Druid requires data to have a primary timestamp column (internally stored in a column called `__time`). If you do not have a timestamp in your data, select `Constant value`. In our example, the data loader determines that the `time` column is the only candidate that can be used as the primary time column.

3. Click **Next: Transform**, **Next: Filter**, and then **Next: Configure schema**, skipping a few steps.

   You do not need to adjust transformation or filtering settings, as applying ingestion time transforms and filters are out of scope for this tutorial.

4. The Configure schema settings are where you configure what [dimensions](https://druid.apache.org/docs/latest/ingestion/data-model.html#dimensions) and [metrics](https://druid.apache.org/docs/latest/ingestion/data-model.html#metrics) are ingested. The outcome of this configuration represents exactly how the data will appear in Druid after ingestion.

   Since our dataset is very small, you can turn off [rollup](https://druid.apache.org/docs/latest/ingestion/rollup.html) by unsetting the **Rollup** switch and confirming the change when prompted.

   ![Data loader schema](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-05.png)

1. Click **Next: Partition** to configure how the data will be split into segments. In this case, choose `DAY` as the **Segment granularity**.

   ![Data loader partition](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-06.png)

   Since this is a small dataset, we can have just a single segment, which is what selecting `DAY` as the segment granularity gives us.

2. Click **Next: Tune** and **Next: Publish**.

3. The Publish settings are where you specify the datasource name in Druid. Let's change the default name from `wikiticker-2015-09-12-sampled` to `wikipedia`.

   ![Data loader publish](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-07.png)

1. Click **Next: Edit spec** to review the ingestion spec we've constructed with the data loader.

   ![Data loader spec](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-08.png)

   Feel free to go back and change settings from previous steps to see how doing so updates the spec. Similarly, you can edit the spec directly and see it reflected in the previous steps.

   > For other ways to load ingestion specs in Druid, see [Tutorial: Loading a file](https://druid.apache.org/docs/latest/tutorials/tutorial-batch.html).

2. Once you are satisfied with the spec, click **Submit**.

   The new task for our wikipedia datasource now appears in the Ingestion view.

   ![Tasks view](https://druid.apache.org/docs/latest/assets/tutorial-batch-data-loader-09.png)

   The task may take a minute or two to complete. When done, the task status should be "SUCCESS", with the duration of the task indicated. Note that the view is set to automatically refresh, so you do not need to refresh the browser to see the status change.

   A successful task means that one or more segments have been built and are now picked up by our data servers.