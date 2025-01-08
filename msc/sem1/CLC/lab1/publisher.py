"""Publisher module

Run with:
    python publisher.py
"""

import time
from random import randint, uniform

import paho.mqtt.client as mqtt


TOPIC_1 = "home/temperature/bedroom"
TOPIC_2 = "factory/machine/alerts"
TOPIC_3 = "bank/transaction/updates"
TOPICS = [TOPIC_1, TOPIC_2, TOPIC_3]
BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883


class Publisher:
    """Publisher class for paho-mqtt"""

    def __init__(self, host, port, topic, qos=0):
        self.host = host
        self.port = port
        self.topic = topic
        self.qos = qos
        self.client = mqtt.Client()
        self.client.connect(self.host, self.port)

    def publish(self, message):
        """Publishes message to topic"""
        self.client.publish(self.topic, qos=self.qos, payload=message)

    def start(self):
        """Starts the publisher"""
        self.client.loop_forever()


def run_publishers():
    publisher1 = Publisher(BROKER_HOST, BROKER_PORT, TOPIC_1, qos=0)
    publisher2 = Publisher(BROKER_HOST, BROKER_PORT, TOPIC_2, qos=1)
    publisher3 = Publisher(BROKER_HOST, BROKER_PORT, TOPIC_3, qos=2)

    while True:
        topic_1_data = round(uniform(15, 25), 2)
        topic_2_data = round(uniform(0, 100), 2)
        topic_3_data = round(uniform(10.0, 1000.0), 2)
        publisher1.publish(topic_1_data)
        publisher2.publish(topic_2_data)
        publisher3.publish(topic_3_data)

        print(f"Published {topic_1_data} to {TOPIC_1}")
        print(f"Published {topic_2_data} to {TOPIC_2}")
        print(f"Published {topic_3_data} to {TOPIC_3}")

        time.sleep(randint(1, 5))


if __name__ == "__main__":
    run_publishers()
