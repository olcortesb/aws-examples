import json
import os
import sys


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Lambda Self-Managed Code Storage working!",
            "storage_mode": os.environ.get("STORAGE_MODE", "unknown"),
            "runtime": sys.version,
            "function_name": context.function_name,
            "function_version": context.function_version,
            "code_bucket": os.environ.get("CODE_BUCKET", "unknown"),
        })
    }
