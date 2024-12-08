# Dockerfile for the MQTT client
FROM python:3.8

WORKDIR /app

COPY ./mqtt_client.py /app

RUN pip install paho-mqtt

CMD ["python", "./mqtt_client.py"]
