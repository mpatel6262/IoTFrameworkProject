# IoTFrameworkProject

## Steps to set up the initial pipeline:
1. Install java, zookeeper, and kafka
**mac with homebrew**
```
$ brew cask install java
$ brew install zookeeper
$ brew install kafka
```
2. Start zookeeper
```
$ zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties
```
3. Start kafka cluster
```
$ kafka-server-start /usr/local/etc/kafka/server.properties
```
4. Create a kafka cluster topic
```
$ kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic {NAME}
```
5. Run **mqttPublisher.py** to publish data periodically to a public mqtt broker
```
$ python3 mqttPublisher.py
```
6. Run **mqttSubscriberAndKafkaPublisher.py** to listen to the public mqtt broker and publish to kafka
```
$ python3 mqttSubscriberAndKafkaPublisher.py
```
