"""Full CRUD test — exercises all DynamoDB operations. Does NOT delete the table."""

import sys
sys.path.insert(0, "/app/scripts" if __package__ is None else ".")
from common import dynamodb, client, ENDPOINT

TABLE = "TestTable"


def ensure_table():
    print("\n=== EnsureTable ===")
    existing = client.list_tables()["TableNames"]
    if TABLE in existing:
        print(f"  Table '{TABLE}' already exists")
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
    print(f"  Table '{TABLE}' created")


def put_items():
    print("\n=== PutItem ===")
    table = dynamodb.Table(TABLE)
    items = [
        {"pk": "user#1", "sk": "profile", "name": "Alice", "age": 30},
        {"pk": "user#1", "sk": "order#001", "total": "49.99", "status": "shipped"},
        {"pk": "user#2", "sk": "profile", "name": "Bob", "age": 25},
    ]
    for item in items:
        table.put_item(Item=item)
        print(f"  Put: {item['pk']} / {item['sk']}")


def get_item():
    print("\n=== GetItem ===")
    table = dynamodb.Table(TABLE)
    resp = table.get_item(Key={"pk": "user#1", "sk": "profile"})
    print(f"  Got: {resp.get('Item')}")


def update_item():
    print("\n=== UpdateItem ===")
    table = dynamodb.Table(TABLE)
    resp = table.update_item(
        Key={"pk": "user#1", "sk": "profile"},
        UpdateExpression="SET age = :val",
        ExpressionAttributeValues={":val": 31},
        ReturnValues="ALL_NEW",
    )
    print(f"  Updated: {resp['Attributes']}")


def query_items():
    print("\n=== Query ===")
    table = dynamodb.Table(TABLE)
    resp = table.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "user#1"},
    )
    print(f"  Found {resp['Count']} items for user#1:")
    for item in resp["Items"]:
        print(f"    {item}")


def scan_table():
    print("\n=== Scan ===")
    table = dynamodb.Table(TABLE)
    resp = table.scan()
    print(f"  Total items in table: {resp['Count']}")


def batch_write():
    print("\n=== BatchWriteItem ===")
    items = [{"pk": "batch#1", "sk": f"item#{i}", "data": f"value_{i}"} for i in range(5)]
    request_items = {
        TABLE: [
            {"PutRequest": {"Item": {"pk": {"S": item["pk"]}, "sk": {"S": item["sk"]}, "data": {"S": item["data"]}}}}
            for item in items
        ]
    }
    client.batch_write_item(RequestItems=request_items)
    print("  Wrote 5 items in batch")


def batch_get():
    print("\n=== BatchGetItem ===")
    keys = [{"pk": "batch#1", "sk": "item#0"}, {"pk": "batch#1", "sk": "item#1"}]
    resp = dynamodb.batch_get_item(RequestItems={TABLE: {"Keys": keys}})
    items = resp.get("Responses", {}).get(TABLE, [])
    print(f"  Got {len(items)} items in batch")


def transact_write():
    print("\n=== TransactWriteItems ===")
    client.transact_write_items(
        TransactItems=[
            {"Put": {"TableName": TABLE, "Item": {"pk": {"S": "tx#1"}, "sk": {"S": "a"}, "val": {"S": "hello"}}}},
            {"Put": {"TableName": TABLE, "Item": {"pk": {"S": "tx#1"}, "sk": {"S": "b"}, "val": {"S": "world"}}}},
        ]
    )
    print("  Transaction committed (2 puts)")


def delete_item():
    print("\n=== DeleteItem ===")
    table = dynamodb.Table(TABLE)
    table.delete_item(Key={"pk": "user#2", "sk": "profile"})
    print("  Deleted user#2/profile")


def main():
    print("=" * 50)
    print("ExtendDB — Full CRUD Test")
    print("=" * 50)
    print(f"Endpoint: {ENDPOINT}")

    ensure_table()
    put_items()
    get_item()
    update_item()
    query_items()
    scan_table()
    batch_write()
    batch_get()
    transact_write()
    delete_item()

    print("\n" + "=" * 50)
    print("✓ All CRUD tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
