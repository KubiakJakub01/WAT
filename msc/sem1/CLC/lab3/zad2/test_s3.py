import os

import boto3
import requests
from requests_aws4auth import AWS4Auth

API_BASE_URL = "https://bpw5dgjaki.execute-api.eu-north-1.amazonaws.com/s3"
AWS_REGION = "eu-north-1"
BUCKET_NAME = "user-26-bucket"


session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=AWS_REGION,
)
credentials = session.get_credentials()
access_key = credentials.access_key
secret_key = credentials.secret_key

auth = AWS4Auth(access_key, secret_key, AWS_REGION, "execute-api")


def test_show_files():
    data = {"body": {"bucket_name": BUCKET_NAME}}

    response = requests.get(API_BASE_URL, auth=auth, json=data)

    print("\nSHOW FILES (GET) Response:")
    print("Status Code:", response.status_code)
    print("Body:", response.json())


def test_find_file(file_name):
    data = {
        "body": {"bucket_name": BUCKET_NAME, "file_name": file_name},
    }

    response = requests.post(API_BASE_URL, auth=auth, json=data)

    print("\nFIND FILE (HEAD) Response:")
    print("Status Code:", response.status_code)
    print("Headers:", response.headers)
    if response.status_code == 200:
        print(f"Plik '{file_name}' istnieje w bucket '{BUCKET_NAME}'.")
    else:
        print(f"Plik '{file_name}' NIE został znaleziony.")


if __name__ == "__main__":
    print("Testing Show Files function...")
    test_show_files()

    print("\nTesting Find File function...")
    test_find_file("users.tsv")
