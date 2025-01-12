import argparse

import boto3


def get_args():
    parser = argparse.ArgumentParser(description="Upload data to DynamoDB")
    parser.add_argument("--id", type=int, required=True, help="ID of the text")
    parser.add_argument(
        "--output_file", default="output.mp3", type=str, help="Output file"
    )
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
    polly = boto3.client(
        "polly",
        region_name=args.region,
        aws_access_key_id=args.aws_access_key_id,
        aws_secret_access_key=args.aws_secret_access_key,
    )

    table = dynamodb.Table(args.table)

    def generate_audio(item_id, output_file):
        response = table.get_item(Key={"ID": item_id})
        text = response["Item"]["Text"]

        polly_response = polly.synthesize_speech(
            Text=text, OutputFormat="mp3", VoiceId="Joanna"
        )

        with open(output_file, "wb") as file:
            file.write(polly_response["AudioStream"].read())
        print(f"Nagrano {output_file}")

    generate_audio(args.id, args.output_file)


if __name__ == "__main__":
    main()
