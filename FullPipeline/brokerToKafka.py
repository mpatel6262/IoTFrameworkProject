import paho.mqtt.client as mqtt
from pykafka import KafkaClient
import json
import time

mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("Smartphone")
client.connect(mqttBroker)

kafka_client = KafkaClient(hosts="localhost:9092")
kafka_topic = kafka_client.topics['TISENSORTAGDATA']
kafka_producer = kafka_topic.get_sync_producer()

def isCorrectFormat(message):
    msg_dict = json.loads(message)
    if (msg_dict.get("system_id") is not None) and (msg_dict.get("model_number") is not None) and (msg_dict.get("battery_level") is not None) and (msg_dict.get("ambient_temperature") is not None) and (msg_dict.get("humidity") is not None) and (msg_dict.get("pressure") is not None) and (msg_dict.get("light") is not None):
        if(len(msg_dict) == 7):
            return True
    return False


def on_message(client, userdata, message):
    msg_payload = str(message.payload.decode("utf-8"))
    print("Received message: ", msg_payload)
    kafka_producer.produce(msg_payload.encode("utf-8"))
    print("KAFKA: Just published " + msg_payload + " to topic TISENSORTAGDATA")


client.subscribe("TISENSORTAGDATA")
client.on_message = on_message

client.loop_forever()
