"""Shared boto3 connection for all scripts. Works inside Docker and on the host."""

import os
import urllib3
import boto3
from botocore.config import Config

# Suppress SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load credentials from shared volume if available (Docker)
CREDS_FILE = "/shared/credentials.env"
if os.path.exists(CREDS_FILE):
    with open(CREDS_FILE) as f:
        for line in f:
            key, _, value = line.strip().partition("=")
            if key and value:
                os.environ.setdefault(key, value)

# Auto-detect: inside Docker uses extenddb hostname, outside uses localhost
DEFAULT_ENDPOINT = "https://extenddb:8000" if os.path.exists(CREDS_FILE) else "https://localhost:8000"

ENDPOINT = os.environ.get("ENDPOINT_URL", DEFAULT_ENDPOINT)
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
    region_name=REGION,
)

dynamodb = session.resource(
    "dynamodb",
    endpoint_url=ENDPOINT,
    verify=False,
    config=Config(retries={"max_attempts": 3, "mode": "standard"}),
)

client = session.client(
    "dynamodb",
    endpoint_url=ENDPOINT,
    verify=False,
    config=Config(retries={"max_attempts": 3, "mode": "standard"}),
)
