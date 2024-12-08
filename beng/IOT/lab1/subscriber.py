'''Subscriber module

Run with:
    python subscriber.py
'''
import threading

import paho.mqtt.client as mqtt

from publisher import TOPIC_1, TOPIC_2, TOPIC_3


class Subscriber:
    '''Subscriber class for paho-mqtt'''
    def __init__(self, host, port, topic, qos=0):
        self.host = host
        self.port = port
        self.topic = topic
        self.qos = qos
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.host, self.port)
        self.data = {}

    def on_connect(self, client, userdata, flags, rc):
        '''On connect callback'''
        print(f'Subscriber {self} connected with result code {rc}')
        self.client.subscribe(self.topic, qos=self.qos)

    def on_message(self, client, userdata, msg):
        '''On message callback'''
        print(f'Subscriber {self} got message {msg.payload} for topic {msg.topic}')
        self.data[msg.topic] = msg.payload.decode()

    def start(self):
        '''Starts the subscriber'''
        self.client.loop_forever()

    def get_data(self, topic):
        '''Returns the data'''
        return self.data.get(topic, f'No {topic} data')

    def __repr__(self) -> str:
        return f'Subscriber(host={self.host}, port={self.port}, topic={self.topic}, qos={self.qos})'
    
    def __str__(self) -> str:
        return f'Subscriber(host={self.host}, port={self.port}, topic={self.topic}, qos={self.qos})'


def run_subscriber(host, port, topic, qos=0):
    # Create and start subscriber
    subscriber = Subscriber(host, port, topic, qos)
    subscriber.start()

def run_subscribers():
    # Run subscribers in separate threads
    subscriber1 = threading.Thread(target=run_subscriber, args=('localhost', 1883, TOPIC_1, 0))
    subscriber2 = threading.Thread(target=run_subscriber, args=('localhost', 1883, TOPIC_2, 1))
    subscriber3 = threading.Thread(target=run_subscriber, args=('localhost', 1883, TOPIC_3, 2))
    subscriber1.start()
    subscriber2.start()
    subscriber3.start()


if __name__ == "__main__":
    run_subscribers()
