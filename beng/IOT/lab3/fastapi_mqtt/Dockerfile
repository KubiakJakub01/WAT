# Dockerfile for the application
FROM python:3.8

WORKDIR /app

COPY ./mqtt_fastapi_client.py /app

RUN pip install paho-mqtt requests

CMD ["python", "./mqtt_fastapi_client.py"]
