'''Publisher module

Run with:
    python publisher.py
'''
import time
from random import randint, uniform

import paho.mqtt.client as mqtt


# Init three topics
TOPIC_1 = 'sensor/home/temperature'
TOPIC_2 = 'sensor/home/humidity'
TOPIC_3 = 'sensor/office/pressure'


class Publisher:
    '''Publisher class for paho-mqtt'''
    def __init__(self, host, port, topic, qos=0):
        self.host = host
        self.port = port
        self.topic = topic
        self.qos = qos
        self.client = mqtt.Client()
        self.client.connect(self.host, self.port)

    def publish(self, message):
        '''Publishes message to topic'''
        self.client.publish(self.topic, qos=self.qos, payload=message)

    def start(self):
        '''Starts the publisher'''
        self.client.loop_forever()


def run_publishers():
    # Create and start publishers
    publisher1 = Publisher('localhost', 1883, TOPIC_1, qos=0)
    publisher2 = Publisher('localhost', 1883, TOPIC_2, qos=1)
    publisher3 = Publisher('localhost', 1883, TOPIC_3, qos=2)

    # Publish some random messages in a loop
    while True:
        temerature = uniform(15, 25)
        humidity = uniform(30, 60)
        pressure = uniform(1000, 1020)
        publisher1.publish(temerature)
        publisher2.publish(humidity)
        publisher3.publish(pressure)

        print(f'Published {temerature} to {TOPIC_1}')
        print(f'Published {humidity} to {TOPIC_2}')
        print(f'Published {pressure} to {TOPIC_3}')

        time.sleep(randint(1, 5))


if __name__ == "__main__":
    run_publishers()
