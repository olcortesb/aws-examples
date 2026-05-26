"""Cleanup — deletes test tables."""

import sys
sys.path.insert(0, "/app/scripts" if __package__ is None else ".")
from common import dynamodb, client, ENDPOINT

TABLES_TO_DELETE = ["TestTable", "LoadTest", "SmokeTest"]


def main():
    print(f"Cleanup against {ENDPOINT}")
    existing = client.list_tables()["TableNames"]

    for table_name in TABLES_TO_DELETE:
        if table_name in existing:
            table = dynamodb.Table(table_name)
            table.delete()
            table.wait_until_not_exists()
            print(f"  Deleted '{table_name}'")
        else:
            print(f"  '{table_name}' not found, skipping")

    print("\n✓ Cleanup complete")


if __name__ == "__main__":
    main()
