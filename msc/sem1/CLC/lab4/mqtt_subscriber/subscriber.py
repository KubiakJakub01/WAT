import logging
import os

import paho.mqtt.client as mqtt
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("subscriber")


MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "test/etap1/polish_example")

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "fastapi_app")
FASTAPI_PORT = os.getenv("FASTAPI_PORT", "80")
FASTAPI_ENDPOINT = os.getenv("FASTAPI_ENDPOINT", "/items")


def on_connect(client, userdata, flags, rc):
    logger.info(f"[SUBSCRIBER] Połączono z brokerem MQTT, kod zwrotny = {rc}")
    client.subscribe(MQTT_TOPIC)
    logger.info(f"[SUBSCRIBER] Zasubskrybowano topic: {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    logger.info(f"[SUBSCRIBER] Otrzymano wiadomość z topica {msg.topic}: {payload}")

    url = f"http://{FASTAPI_HOST}:{FASTAPI_PORT}{FASTAPI_ENDPOINT}"
    logger.info(f"[SUBSCRIBER] Wysyłam żądanie POST do FastAPI: {url}")
    try:
        resp = requests.post(url, json={"mqtt_message": payload})
        logger.info(f"[SUBSCRIBER] Odpowiedź FastAPI: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.info(f"[SUBSCRIBER] Błąd podczas wysyłania żądania do FastAPI: {e}")


def main():
    client = mqtt.Client("subscriber-etap1")
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_forever()

if __name__ == "__main__":
    main()
