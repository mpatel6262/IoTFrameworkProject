from pyspark.sql import SparkSession

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
# For this example, we'll simply write the data to another Kafka topic.
query = kafkaStream.writeStream \
    .outputMode("append") \
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
