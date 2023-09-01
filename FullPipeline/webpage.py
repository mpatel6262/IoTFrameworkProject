from flask import Flask, render_template, jsonify
from astrapy.rest import create_client, http_methods
from threading import Thread
import time
import uuid
import os

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

app = Flask(__name__)

responseDict = {}

def poll_cassandra():
    global responseDict
    while True:
        response = astra_http_client.request(
            method=http_methods.GET,
            path=f"/api/rest/v2/keyspaces/{ASTRA_DB_KEYSPACE}/{COLLECTION_NAME}/rows")
        
        responseDict = response.get("data")
        time.sleep(5)  

@app.route('/')
def index():
    return render_template('index.html', response=responseDict)

@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify(responseDict)

if __name__ == '__main__':
    astra_http_client = create_client(astra_database_id=ASTRA_DB_ID,
      astra_database_region=ASTRA_DB_REGION,
      astra_application_token=ASTRA_DB_APPLICATION_TOKEN)
    
 
    poll_thread = Thread(target=poll_cassandra)
    poll_thread.daemon = True 
    poll_thread.start()

    app.run()
