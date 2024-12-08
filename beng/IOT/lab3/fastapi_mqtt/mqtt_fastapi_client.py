import json
import logging

import paho.mqtt.client as mqtt
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MQTT_BROKER = 'mqtt-broker'
FASTAPI_URL = 'http://fastapi-service:8000/data'
TOPIC_SUBSCRIBE = 'request/data'
TOPIC_PUBLISH = 'response/data'

def on_connect(client, userdata, flags, rc):
    logger.info('Connected with result code ' + str(rc))
    client.subscribe(TOPIC_SUBSCRIBE)

def on_message(client, userdata, msg):
    if msg.topic == TOPIC_SUBSCRIBE:
        response = requests.get(FASTAPI_URL)
        data = response.json()
        client.publish(TOPIC_PUBLISH, json.dumps(data))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

if __name__ == '__main__':
    logger.info('Starting MQTT-FASTAPI client...')
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()
