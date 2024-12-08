import logging

import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MQTT_BROKER = 'mqtt-broker'
TOPIC = 'response/data'

def on_connect(client, userdata, flags, rc):
    logger.info('Connected with result code ' + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    logger.info(f'Received message: {msg.payload.decode()} on topic {msg.topic}')


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


if __name__ == '__main__':
    logger.info('Starting MQTT client...')
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()
