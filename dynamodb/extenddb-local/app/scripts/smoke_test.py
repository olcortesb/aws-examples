"""Smoke test — quick validation that ExtendDB is working."""

import sys
sys.path.insert(0, "/app/scripts" if __package__ is None else ".")
from common import dynamodb, client, ENDPOINT

TABLE = "SmokeTest"


def main():
    print(f"Smoke test against {ENDPOINT}")

    # Create table if not exists
    existing = client.list_tables()["TableNames"]
    if TABLE not in existing:
        dynamodb.create_table(
            TableName=TABLE,
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        dynamodb.Table(TABLE).wait_until_exists()
        print(f"  Created table '{TABLE}'")

    # Put + Get
    table = dynamodb.Table(TABLE)
    table.put_item(Item={"pk": "smoke", "status": "ok"})
    resp = table.get_item(Key={"pk": "smoke"})
    item = resp.get("Item", {})

    assert item.get("status") == "ok", f"Unexpected item: {item}"
    print("  PutItem + GetItem: OK")

    # Cleanup item (not table)
    table.delete_item(Key={"pk": "smoke"})
    print("  DeleteItem: OK")
    print("\n✓ Smoke test passed")


if __name__ == "__main__":
    main()
