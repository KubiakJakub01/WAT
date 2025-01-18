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
    return parser.parse_args()


def load_config(config_fp: Path):
    with open(config_fp, 'r', encoding='utf-8') as f:
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
            host=host,
            database=database,
            user=user,
            password=password
        )
        cursor = connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Tabela została utworzona!")

    except Exception as e:
        print(f"Błąd: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Połączenie z bazą zostało zamknięte.")


if __name__ == "__main__":
    main()
