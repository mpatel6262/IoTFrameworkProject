# IoTFrameworkProject

## Steps to set up the initial pipeline:
1. Install java, zookeeper, apache-spark and kafka
**mac with homebrew**
```
$ brew cask install java
$ brew install zookeeper
$ brew install Kafka
$ brew install apache-spark
```
2. Start zookeeper
```
$ zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties
```
3. Start kafka cluster
```
$ kafka-server-start /usr/local/etc/kafka/server.properties
```
4. Create a Kafka cluster topic
```
$ kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic {NAME 1}
```
5. Run **mqttPublisher.py** to publish data periodically to a public MQTT broker
```
$ python3 mqttPublisher.py
```
6. Run **mqttSubscriberAndKafkaPublisher.py** to listen to the public MQTT broker and publish to Kafka
```
$ python3 mqttSubscriberAndKafkaPublisher.py
```

## Setting up PySpark structured streaming:
***Prerequisite: Set up the SPARK_HOME env variable in .zshrc***

7. Create another Kafka topic to ingest output events from the PySpark script as done in step 4
```
$ kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic {NAME 2}
```
8. Submit the PySpark script to the spark
```
$ spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 --master local pySparkJob.py
```
***Note: Make sure to update the REPLACE_ME items in the files***

## Optional testing of the PySpark script
1. Set up a producer that publishes to your first topic
```
$ kafka-console-producer -broker-list localhost:9092 -topic {NAME 1}
```
3. Set up a consumer to read from the second topic you created
```
$ kafka-console-consumer -bootstrap-server localhost:9092 -topic {NAME 2}
```

