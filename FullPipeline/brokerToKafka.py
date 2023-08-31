import paho.mqtt.client as mqtt
from pykafka import KafkaClient
import time

mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("Smartphone")
client.connect(mqttBroker)

kafka_client = KafkaClient(hosts="localhost:9092")
kafka_topic = kafka_client.topics['TISENSORTAGDATA']
kafka_producer = kafka_topic.get_sync_producer()

def on_message(client, userdata, message):
    msg_payload = str(message.payload.decode("utf-8"))
    print("Received message: ", msg_payload)
    kafka_producer.produce(msg_payload.encode("utf-8"))
    print("KAFKA: Just published " + msg_payload + " to topic TISENSORTAGDATA")


client.subscribe("TISENSORTAGDATA")
client.on_message = on_message

client.loop_forever()
