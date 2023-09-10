from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, avg

# Step 1: Create a Spark session
spark = SparkSession.builder \
    .appName("IoTKafkaStructuredStreaming") \
    .getOrCreate()

# Step 2: Configure Kafka connection
kafka_brokers = "localhost:9092"  # Replace with your Kafka broker address
kafka_input_topic = "REPLACE_ME"  # Replace with the Kafka topic you want to consume
kafka_output_topic = "REPLACE_ME"  # Replace with the Kafka topic where you want to output data

# Step 3: Define Kafka source for Structured Streaming
kafkaStream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", kafka_input_topic) \
    .load()

# Step 4: Process the Kafka stream
kafkaStream = kafkaStream.selectExpr("CAST(value AS STRING)")

# Step 5: Define your processing logic (if needed)
# For this example, we'll calculate the average for each specific topic.
aggregatedStream = kafkaStream.selectExpr(
    "CAST(value AS STRING) as message",
    "split(value, ',')[0] as topic",
    "cast(split(value, ',')[1] as int) as value"
).groupBy("topic").agg(avg("value").alias("average_value"))

# Step 6: Write the average values to another Kafka topic
query = aggregatedStream.selectExpr("topic", "cast(average_value as string) as value") \
    .writeStream \
    .outputMode("complete") \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("topic", kafka_output_topic) \
    .option("checkpointLocation", "/Users/macbook/Projects/IoTFrameworkProject/output") \
    .start()

# Step 6: Start the Structured Streaming query
query.awaitTermination()

# Step 7: Gracefully stop the application (optional)
def stop_app():
    query.stop()
    spark.stop()

query.awaitTermination()
