import os

import boto3
import requests
from requests_aws4auth import AWS4Auth

API_BASE_URL = "https://6wkyutdslh.execute-api.eu-north-1.amazonaws.com/dynamodb"
AWS_REGION = "eu-north-1"

session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)
credentials = session.get_credentials()
access_key = credentials.access_key
secret_key = credentials.secret_key

auth = AWS4Auth(access_key, secret_key, AWS_REGION, "execute-api")


def test_post():
    data = {"body": {"ID": 1, "name": "John Doe", "email": "john.doe@example.com"}}

    response = requests.post(API_BASE_URL, auth=auth, json=data)
    print("POST Response:")
    print("Status Code:", response.status_code)
    print("Body:", response.json())


def test_get():
    data = {"body": {"ID": 1}}

    response = requests.get(API_BASE_URL, auth=auth, json=data)
    print("GET Response:")
    print("Status Code:", response.status_code)
    print("Body:", response.json())


if __name__ == "__main__":
    print("Testing POST function...")
    test_post()

    print("\nTesting GET function...")
    test_get()
