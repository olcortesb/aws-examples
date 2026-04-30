import json
import os
import time

MOUNT_PATH = os.environ.get('MOUNT_PATH', '/mnt/s3files')


def lambda_handler(event, context):
    """Test S3 Files mount operations"""

    # Function URL sends body as string
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
    """Write a file to the mounted S3 bucket"""

    filename = event.get('filename', 'test.txt')
    content = event.get('content', f'Hello from Lambda! Timestamp: {time.time()}')
    filepath = os.path.join(MOUNT_PATH, filename)

    start = time.time()
    with open(filepath, 'w') as f:
        f.write(content)
    elapsed = time.time() - start

    return {
        'operation': 'write',
        'filepath': filepath,
        'size_bytes': len(content),
        'elapsed_ms': round(elapsed * 1000, 2)
    }


def test_read(event):
    """Read a file from the mounted S3 bucket"""

    filename = event.get('filename', 'test.txt')
    filepath = os.path.join(MOUNT_PATH, filename)

    if not os.path.exists(filepath):
        return {'operation': 'read', 'error': f'File not found: {filepath}'}

    start = time.time()
    with open(filepath, 'r') as f:
        content = f.read()
    elapsed = time.time() - start

    return {
        'operation': 'read',
        'filepath': filepath,
        'size_bytes': len(content),
        'content': content[:500],
        'elapsed_ms': round(elapsed * 1000, 2)
    }


def test_list(event):
    """List files in the mounted S3 bucket"""

    subdir = event.get('subdir', '')
    dirpath = os.path.join(MOUNT_PATH, subdir)

    if not os.path.exists(dirpath):
        return {'operation': 'list', 'error': f'Directory not found: {dirpath}'}

    start = time.time()
    entries = []
    for entry in os.listdir(dirpath):
        full_path = os.path.join(dirpath, entry)
        entries.append({
            'name': entry,
            'is_dir': os.path.isdir(full_path),
            'size_bytes': os.path.getsize(full_path) if os.path.isfile(full_path) else 0
        })
    elapsed = time.time() - start

    return {
        'operation': 'list',
        'dirpath': dirpath,
        'count': len(entries),
        'entries': entries,
        'elapsed_ms': round(elapsed * 1000, 2)
    }


def test_delete(event):
    """Delete a file from the mounted S3 bucket"""

    filename = event.get('filename', 'test.txt')
    filepath = os.path.join(MOUNT_PATH, filename)

    if not os.path.exists(filepath):
        return {'operation': 'delete', 'error': f'File not found: {filepath}'}

    start = time.time()
    os.remove(filepath)
    elapsed = time.time() - start

    return {
        'operation': 'delete',
        'filepath': filepath,
        'elapsed_ms': round(elapsed * 1000, 2)
    }


def test_all(event):
    """Run all operations sequentially"""

    results = []

    # Write
    results.append(test_write({
        'filename': 'test_all.txt',
        'content': f'Full test at {time.time()}'
    }))

    # List
    results.append(test_list({}))

    # Read
    results.append(test_read({'filename': 'test_all.txt'}))

    # Delete
    results.append(test_delete({'filename': 'test_all.txt'}))

    return {'operation': 'all', 'results': results}
