
# Sending Data from S3 to Kafka using AWS Glue and Spark

## Version 1: Sending Avro Data

### Overview:
This solution provides a method to read Avro files from multiple S3 paths into a Spark DataFrame and then send each object from these files as a separate message to a Kafka topic in Avro format.

### Steps:

1. **Setup Spark Session**: 
Initialize a Spark session which is the entry point to any Spark functionality.

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("GlueKafkaAvroIntegration").getOrCreate()
```

2. **Specify S3 Paths**:
List down the S3 paths where your Avro files reside.

```python
s3_paths = [
    "s3://your-bucket/path1/",
    "s3://your-bucket/path2/",
    # ... add more paths as needed
]
```

3. **Read Avro files into a DataFrame**: 
Utilize Spark's `read.format("avro")` method to read the content of the S3 paths into a DataFrame.

```python
dfs = [spark.read.format("avro").load(path) for path in s3_paths]
```

4. **Combine Multiple DataFrames**: 
Combine the DataFrames from each path into one.

```python
from functools import reduce
combined_df = reduce(lambda a, b: a.union(b), dfs)
```

5. **Write DataFrame to Kafka in Avro Format**: 
Convert each row of the DataFrame to Avro format and send to the specified Kafka topic.

```python
kafka_servers = 'your.kafka.bootstrap.servers'
topic_name = "your_topic_name"

combined_df.selectExpr("to_avro(struct(*)) AS value") \
     .write.format("kafka") \
     .option("kafka.bootstrap.servers", kafka_servers) \
     .option("topic", topic_name) \
     .option("kafka.security.protocol", "SSL") \
     .option("kafka.ssl.key.location", "/path/to/service.key") \
     .option("kafka.ssl.certificate.location", "/path/to/service.cert") \
     .option("kafka.ssl.truststore.location", "/path/to/ca.pem") \
     .save()
```

## Version 2: Sending JSON Data

### Overview:
This solution provides a method to read JSON files from multiple S3 paths into a Spark DataFrame and then send each JSON object (or line) from these files as a separate message to a Kafka topic.

### Steps:

1. **Setup Spark Session**: 
Initialize a Spark session which is the entry point to any Spark functionality.

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("GlueKafkaJSONIntegration").getOrCreate()
```

2. **Specify S3 Paths**:
List down the S3 paths where your JSON files reside.

```python
s3_paths = [
    "s3://your-bucket/path1/",
    "s3://your-bucket/path2/",
    # ... add more paths as needed
]
```

3. **Read JSON files into a DataFrame**: 
Utilize Spark's `read.json` method to read the content of the S3 paths into a DataFrame.

```python
dfs = [spark.read.json(path) for path in s3_paths]
```

4. **Combine Multiple DataFrames**: 
Combine the DataFrames from each path into one.

```python
from functools import reduce
combined_df = reduce(lambda a, b: a.union(b), dfs)
```

5. **Write DataFrame to Kafka**: 
Each row of the DataFrame (which corresponds to a JSON object) is sent as a separate message to the specified Kafka topic.

```python
kafka_servers = 'your.kafka.bootstrap.servers'
topic_name = "your_topic_name"

combined_df.selectExpr("CAST(value AS STRING)") \
     .write.format("kafka") \
     .option("kafka.bootstrap.servers", kafka_servers) \
     .option("topic", topic_name) \
     .option("kafka.security.protocol", "SSL") \
     .option("kafka.ssl.key.location", "/path/to/service.key") \
     .option("kafka.ssl.certificate.location", "/path/to/service.cert") \
     .option("kafka.ssl.truststore.location", "/path/to/ca.pem") \
     .save()
```


## Complete Code for Sending Avro Data from S3 to Kafka:

```python
from pyspark.sql import SparkSession
from functools import reduce

spark = SparkSession.builder.appName("GlueKafkaAvroIntegration").getOrCreate()

s3_paths = [
    "s3://your-bucket/path1/",
    "s3://your-bucket/path2/",
    # ... add more paths as needed
]

dfs = [spark.read.format("avro").load(path) for path in s3_paths]

combined_df = reduce(lambda a, b: a.union(b), dfs)

kafka_servers = 'your.kafka.bootstrap.servers'
topic_name = "your_topic_name"

combined_df.selectExpr("to_avro(struct(*)) AS value") \
     .write.format("kafka") \
     .option("kafka.bootstrap.servers", kafka_servers) \
     .option("topic", topic_name) \
     .option("kafka.security.protocol", "SSL") \
     .option("kafka.ssl.key.location", "/path/to/service.key") \
     .option("kafka.ssl.certificate.location", "/path/to/service.cert") \
     .option("kafka.ssl.truststore.location", "/path/to/ca.pem") \
     .save()
```

## Complete Code for Sending JSON Data from S3 to Kafka:

```python
from pyspark.sql import SparkSession
from functools import reduce

spark = SparkSession.builder.appName("GlueKafkaJSONIntegration").getOrCreate()

s3_paths = [
    "s3://your-bucket/path1/",
    "s3://your-bucket/path2/",
    # ... add more paths as needed
]

dfs = [spark.read.json(path) for path in s3_paths]

combined_df = reduce(lambda a, b: a.union(b), dfs)

kafka_servers = 'your.kafka.bootstrap.servers'
topic_name = "your_topic_name"

combined_df.selectExpr("CAST(value AS STRING)") \
     .write.format("kafka") \
     .option("kafka.bootstrap.servers", kafka_servers) \
     .option("topic", topic_name) \
     .option("kafka.security.protocol", "SSL") \
     .option("kafka.ssl.key.location", "/path/to/service.key") \
     .option("kafka.ssl.certificate.location", "/path/to/service.cert") \
     .option("kafka.ssl.truststore.location", "/path/to/ca.pem") \
     .save()
```
