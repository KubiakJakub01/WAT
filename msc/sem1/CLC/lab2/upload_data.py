import argparse

import boto3


def get_args():
    parser = argparse.ArgumentParser(description="Upload data to DynamoDB")
    parser.add_argument("--id", type=int, required=True, help="ID of the text")
    parser.add_argument("--text", type=str, help="Text to upload")
    parser.add_argument("--region", default="us-east-2", type=str, help="Region name")
    parser.add_argument("--table", default="User05Texts", type=str, help="Table name")
    parser.add_argument(
        "--aws_access_key_id", type=str, required=False, help="AWS access key ID"
    )
    parser.add_argument(
        "--aws_secret_access_key",
        type=str,
        required=False,
        help="AWS secret access key",
    )
    return parser.parse_args()


def main():
    args = get_args()

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=args.region,
        aws_access_key_id=args.aws_access_key_id,
        aws_secret_access_key=args.aws_secret_access_key,
    )
    table = dynamodb.Table(args.table)

    def add_item(_id, text):
        response = table.put_item(Item={"ID": _id, "Text": text})
        print("Dodano dane:", response)

    add_item(args.id, args.text)


if __name__ == "__main__":
    main()
