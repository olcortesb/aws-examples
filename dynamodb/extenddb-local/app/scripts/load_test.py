"""Load test — generates traffic to populate metrics in the ExtendDB console."""

import sys
import time
import random
import string
sys.path.insert(0, "/app/scripts" if __package__ is None else ".")
from common import dynamodb, client, ENDPOINT

TABLE = "LoadTest"
NUM_ITEMS = int(sys.argv[1]) if len(sys.argv) > 1 else 100
BATCH_SIZE = 25


def random_string(length=20):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def ensure_table():
    existing = client.list_tables()["TableNames"]
    if TABLE in existing:
        return
    dynamodb.create_table(
        TableName=TABLE,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb.Table(TABLE).wait_until_exists()
    print(f"  Created table '{TABLE}'")


def write_load():
    print(f"\n--- Writing {NUM_ITEMS} items in batches of {BATCH_SIZE}...")
    table = dynamodb.Table(TABLE)
    start = time.time()
    written = 0

    for batch_start in range(0, NUM_ITEMS, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, NUM_ITEMS)
        items = []
        for i in range(batch_start, batch_end):
            items.append({
                "PutRequest": {
                    "Item": {
                        "pk": {"S": f"load#{i % 10}"},
                        "sk": {"S": f"item#{i}"},
                        "data": {"S": random_string(50)},
                        "timestamp": {"N": str(int(time.time()))},
                    }
                }
            })
        client.batch_write_item(RequestItems={TABLE: items})
        written += len(items)

    elapsed = time.time() - start
    print(f"  Wrote {written} items in {elapsed:.2f}s ({written/elapsed:.0f} items/s)")


def read_load():
    print(f"\n--- Reading: 10 queries + 5 scans...")
    table = dynamodb.Table(TABLE)
    start = time.time()

    for i in range(10):
        table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": f"load#{i % 10}"},
        )

    for _ in range(5):
        table.scan(Limit=50)

    elapsed = time.time() - start
    print(f"  15 read operations in {elapsed:.2f}s")


def main():
    print("=" * 50)
    print(f"ExtendDB — Load Test ({NUM_ITEMS} items)")
    print("=" * 50)
    print(f"Endpoint: {ENDPOINT}")

    ensure_table()
    write_load()
    read_load()

    # Final stats
    resp = table = dynamodb.Table(TABLE).scan(Select="COUNT")
    print(f"\n  Total items in '{TABLE}': {resp['Count']}")
    print("\n✓ Load test complete — check metrics at https://localhost:8000/console/")


if __name__ == "__main__":
    main()
