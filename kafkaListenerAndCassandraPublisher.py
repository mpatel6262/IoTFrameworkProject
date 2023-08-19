from astrapy.collections import create_client, AstraCollection
import uuid
import os
import time
from kafka import KafkaConsumer

# get Astra connection information from environment variables
ASTRA_DB_ID = os.environ.get('ASTRA_DB_ID')
ASTRA_DB_REGION = os.environ.get('ASTRA_DB_REGION')
ASTRA_DB_APPLICATION_TOKEN = os.environ.get('ASTRA_DB_APPLICATION_TOKEN')
ASTRA_DB_KEYSPACE = os.environ.get('ASTRA_DB_KEYSPACE')

COLLECTION_NAME = "iotdatapipeline"

# setup an Astra Client
astra_client = create_client(astra_database_id=ASTRA_DB_ID,
  astra_database_region=ASTRA_DB_REGION,
  astra_application_token=ASTRA_DB_APPLICATION_TOKEN)
collection = astra_client.namespace(ASTRA_DB_KEYSPACE).collection(COLLECTION_NAME)

# setup a Kafka consumer
consumer = KafkaConsumer(
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     group_id='my-consumer-1',
)

consumer.subscribe(['temperature'])

while True:
    try: 
        message = consumer.poll(10.0)

        print(f"Received message: {message}")

        # create a new document
        cliff_uuid = str(uuid.uuid4())
        print(f'Sending AstraCollection request using namespace: {ASTRA_DB_KEYSPACE}, collection: {COLLECTION_NAME}, and uuid: cliff_uuid')

        response = collection.create(path=cliff_uuid, document={
            "data_from_kafka": str(message),
        })

        print (response)

        time.sleep(120) # Sleep for 2 minutes
    except:
        # Handle any exception here
        print('Exception occurred')
    finally:
        consumer.close()
        print("Goodbye")
