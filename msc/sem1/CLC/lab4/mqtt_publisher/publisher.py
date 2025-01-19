import logging
import os
import time

import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("publisher")


MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "test/etap1/polish_example")


def main():
    client = mqtt.Client("publisher-etap1")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    count = 0
    while True:
        message = f"Hello MQTT {count}"
        logger.info(
            f"[PUBLISHER] Publikuję wiadomość: {message} na topic: {MQTT_TOPIC}"
        )
        client.publish(MQTT_TOPIC, message)
        count += 1
        time.sleep(5)


if __name__ == "__main__":
    main()
