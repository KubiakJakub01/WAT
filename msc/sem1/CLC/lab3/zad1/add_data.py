import argparse
import json
from pathlib import Path

import psycopg2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default="config.json",
        help="Path to the config file.",
    )
    parser.add_argument("--name", type=str, required=True, help="User name to add.")
    parser.add_argument("--email", type=str, required=True, help="User email to add.")
    return parser.parse_args()


def load_config(config_fp: Path):
    with open(config_fp, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    args = parse_args()
    config = load_config(args.config)
    host = config["PostgresDB"]["host"]
    database = config["PostgresDB"]["database"]
    user = config["PostgresDB"]["user"]
    password = config["PostgresDB"]["password"]

    try:
        connection = psycopg2.connect(
            host=host, database=database, user=user, password=password
        )
        print("Połączono z bazą danych!")

        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO users (name, email) VALUES (%s, %s)
        """,
            (args.name, args.email),
        )
        connection.commit()
        print("Dodano użytkownika!")

        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        print("Wszyscy użytkownicy:")
        for row in rows:
            print(row)

    except Exception as e:
        print(f"Błąd podczas łączenia z bazą: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Połączenie z bazą zostało zamknięte.")


if __name__ == "__main__":
    main()
