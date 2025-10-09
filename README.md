# AWS Examples

A comprehensive repository of practical AWS services examples and use cases. This project serves as a hands-on learning resource for exploring different AWS services through real-world implementations.

## Project Structure

The repository is organized by AWS service categories, with each containing practical examples and complete implementations:

```
aws-examples/
├── sqs/                    # Amazon Simple Queue Service examples
│   └── batch-messages/     # SQS batch processing with Lambda
│       ├── get_messages/   # Lambda function code
│       ├── scripts/        # Utility scripts
│       ├── tests/          # Unit and integration tests
│       ├── events/         # Test events
│       ├── template.yaml   # SAM template
│       └── README.md       # Detailed instructions
├── lambda/                 # AWS Lambda examples (coming soon)
├── s3/                     # Amazon S3 examples (coming soon)
├── dynamodb/               # Amazon DynamoDB examples (coming soon)
├── api-gateway/            # Amazon API Gateway examples (coming soon)
└── README.md
```

## Current Examples

### SQS (Simple Queue Service)
- **batch-messages**: Complete serverless application demonstrating SQS message processing in batches using AWS Lambda
  - Manual Lambda invocation for batch processing
  - Utility scripts for sending test messages
  - SAM template for infrastructure as code

## Planned Examples

- **Lambda**: Function patterns, triggers, and best practices
- **S3**: Object storage, event notifications, and lifecycle policies
- **DynamoDB**: NoSQL database operations and patterns
- **API Gateway**: REST and WebSocket APIs
- **CloudFormation/SAM**: Infrastructure as Code templates
- **EventBridge**: Event-driven architectures
- **Step Functions**: Workflow orchestration
- **SNS**: Pub/Sub messaging patterns

## Getting Started

Each example includes:
- Complete source code
- Infrastructure templates (SAM/CloudFormation)
- Deployment instructions
- Testing scripts and utilities
- Detailed README with step-by-step guides

## Prerequisites

- AWS CLI configured with appropriate credentials
- SAM CLI for serverless applications
- Python 3.9+ for Lambda functions
- Docker for local testing

## Usage

1. Navigate to the specific service example you want to explore
2. Follow the README instructions in each example directory
3. Deploy using the provided SAM templates or CloudFormation
4. Test using the included scripts and utilities

## Contributing

This repository is continuously updated with new AWS service examples and use cases. Each example is designed to be:
- pre-Production-ready
- Well-documented
- Following AWS best practices
- Including proper error handling and logging

## Blog Articles

Detailed articles explaining the implementation and concepts behind each example will be published alongside the code examples.
