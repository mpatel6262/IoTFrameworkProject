from astrapy.rest import create_client, http_methods
import json
import uuid
import os
import time
from kafka import KafkaConsumer

"""
Run Following in Terminal (Replace Information):
export ASTRA_DB_ID=32730052-50a5-4fdc-a942-89a60e02c487
export ASTRA_DB_REGION=us-east1
export ASTRA_DB_KEYSPACE=iotdatabase
export ASTRA_DB_APPLICATION_TOKEN=AstraCS:ZxlBhWSnldgOSTSkChYuTlpZ:78ca4bf938f212ce730b2c0f81bc876cb69f5c51756b663d09eae96d66754c18
"""

ASTRA_DB_ID = os.environ.get('ASTRA_DB_ID')
ASTRA_DB_REGION = os.environ.get('ASTRA_DB_REGION')
ASTRA_DB_APPLICATION_TOKEN = os.environ.get('ASTRA_DB_APPLICATION_TOKEN')
ASTRA_DB_KEYSPACE = os.environ.get('ASTRA_DB_KEYSPACE')

COLLECTION_NAME = "sensortaginfo"

astra_http_client = create_client(astra_database_id=ASTRA_DB_ID,
  astra_database_region=ASTRA_DB_REGION,
  astra_application_token=ASTRA_DB_APPLICATION_TOKEN)

consumer = KafkaConsumer(
    'TISENSORTAGDATA',                
    bootstrap_servers='localhost:9092',  
    group_id=None,           
    auto_offset_reset='latest',  
    value_deserializer=lambda x: json.dumps(x.decode('utf-8')))

def parse_string_to_dict(input_string):
    dictionary = {}
    
    input_string = input_string[2:-2]
    parts = input_string.split(', ')
    for part in parts:
        key, value = part.split(': ')
        key = key.replace('\\"', '')
        value = value.replace('\\"', '')
        dictionary[key] = value
    
    return dictionary

for message in consumer:
    input_string = message.value
    parsed_dict = parse_string_to_dict(input_string)
    response = astra_http_client.request(
        method=http_methods.POST,
        path=f"/api/rest/v2/keyspaces/{ASTRA_DB_KEYSPACE}/{COLLECTION_NAME}",
        json_data = parsed_dict)
    print(response)
