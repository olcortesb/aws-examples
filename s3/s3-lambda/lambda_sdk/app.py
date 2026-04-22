import json
import os
import time
import boto3

BUCKET_NAME = os.environ.get('BUCKET_NAME')
PREFIX = 'lambda/'
s3 = boto3.client('s3')


def lambda_handler(event, context):
    """Test S3 SDK operations (traditional approach)"""

    if 'body' in event:
        body = event['body']
        if isinstance(body, str):
            event = json.loads(body)

    operation = event.get('operation', 'all')

    operations = {
        'write': test_write,
        'read': test_read,
        'list': test_list,
        'delete': test_delete,
        'all': test_all
    }

    handler = operations.get(operation, test_all)
    result = handler(event)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(result, indent=2)
    }


def test_write(event):
    """Write a file to S3 using SDK"""

    filename = event.get('filename', 'test.txt')
    content = event.get('content', f'Hello from Lambda! Timestamp: {time.time()}')
    key = f"{PREFIX}{filename}"

    start = time.time()
    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=content.encode())
    elapsed = time.time() - start

    return {
        'operation': 'write',
        'filepath': f's3://{BUCKET_NAME}/{key}',
        'size_bytes': len(content),
        'elapsed_ms': round(elapsed * 1000, 2)
    }


def test_read(event):
    """Read a file from S3 using SDK"""

    filename = event.get('filename', 'test.txt')
    key = f"{PREFIX}{filename}"

    try:
        start = time.time()
        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        content = response['Body'].read().decode()
        elapsed = time.time() - start
    except s3.exceptions.NoSuchKey:
        return {'operation': 'read', 'error': f'File not found: {key}'}

    return {
        'operation': 'read',
        'filepath': f's3://{BUCKET_NAME}/{key}',
        'size_bytes': len(content),
        'content': content[:500],
        'elapsed_ms': round(elapsed * 1000, 2)
    }


def test_list(event):
    """List files in S3 using SDK"""

    subdir = event.get('subdir', '')
    prefix = f"{PREFIX}{subdir}"

    start = time.time()
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    entries = []
    for obj in response.get('Contents', []):
        name = obj['Key'].replace(prefix, '', 1)
        if name:
            entries.append({
                'name': name,
                'is_dir': name.endswith('/'),
                'size_bytes': obj['Size']
            })
    elapsed = time.time() - start

    return {
        'operation': 'list',
        'dirpath': f's3://{BUCKET_NAME}/{prefix}',
        'count': len(entries),
        'entries': entries,
        'elapsed_ms': round(elapsed * 1000, 2)
    }


def test_delete(event):
    """Delete a file from S3 using SDK"""

    filename = event.get('filename', 'test.txt')
    key = f"{PREFIX}{filename}"

    start = time.time()
    s3.delete_object(Bucket=BUCKET_NAME, Key=key)
    elapsed = time.time() - start

    return {
        'operation': 'delete',
        'filepath': f's3://{BUCKET_NAME}/{key}',
        'elapsed_ms': round(elapsed * 1000, 2)
    }


def test_all(event):
    """Run all operations sequentially"""

    results = []

    results.append(test_write({
        'filename': 'test_all.txt',
        'content': f'Full test at {time.time()}'
    }))

    results.append(test_list({}))

    results.append(test_read({'filename': 'test_all.txt'}))

    results.append(test_delete({'filename': 'test_all.txt'}))

    return {'operation': 'all', 'results': results}
