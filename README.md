# AWS Examples

A repository of practical AWS services examples and use cases. Hands-on learning resource for exploring different AWS services through real-world implementations.

## Project Structure

```
aws-examples/
├── dynamodb/
│   └── extenddb-local/         # DynamoDB-compatible local env with ExtendDB (Docker)
├── sqs/
│   └── batch-messages/         # SQS batch processing with Lambda (SAM)
├── s3/
│   └── s3-lambda/              # S3 Files vs SDK benchmark with Lambda (Terraform)
└── README.md
```

## Examples

### DynamoDB - ExtendDB Local
Full DynamoDB-compatible local environment using [ExtendDB](https://github.com/ExtendDB/extenddb) (open source). Three Docker containers: PostgreSQL, ExtendDB server, and a Python app with selectable test scripts.
- No AWS account required
- Full DynamoDB wire protocol compatibility
- Multiple scripts: smoke test, CRUD, load test, cleanup
- Run scripts inside Docker (`docker compose exec`) or locally with virtualenv
- Web management console with metrics at `https://localhost:8000/console/`
- [Read more](dynamodb/extenddb-local/README.md)

### SQS - Batch Messages
Complete serverless application demonstrating SQS message processing in batches using AWS Lambda.
- Manual Lambda invocation for batch processing
- Utility scripts for sending test messages
- SAM template for infrastructure as code
- [Read more](sqs/batch-messages/README.md)

### S3 - S3 Files + Lambda
POC testing Amazon S3 Files (April 2026) integration with Lambda, mounting S3 buckets as local filesystems. Includes a performance benchmark comparing S3 Files (filesystem mount) vs traditional SDK (boto3) approach.
- S3 Files filesystem mounted at `/mnt/s3files`
- Side-by-side Lambda comparison (filesystem vs boto3)
- 100-iteration benchmark with detailed statistics
- Terraform infrastructure as code
- [Read more](s3/s3-lambda/README.md)

## Prerequisites

- AWS CLI configured with appropriate credentials
- SAM CLI for serverless applications
- Terraform >= 1.5.0 for infrastructure as code
- Python 3.9+

## Usage

1. Navigate to the specific service example you want to explore
2. Follow the README instructions in each example directory
3. Deploy using the provided SAM templates or Terraform
4. Test using the included scripts and utilities
