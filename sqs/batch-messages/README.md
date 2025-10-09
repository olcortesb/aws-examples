# bach-messages

This project contains a serverless application that processes SQS messages in batches using AWS Lambda. It includes:

- get_messages/ - Lambda function code for processing SQS messages
- scripts/ - Utility scripts for sending test messages
- events/ - Invocation events for testing
- tests/ - Unit and integration tests
- template.yaml - SAM template defining AWS resources

The application uses AWS Lambda and SQS. The Lambda function can be invoked manually to process batches of messages from the SQS queue.

If you prefer to use an integrated development environment (IDE) to build and test your application, you can use the AWS Toolkit.  
The AWS Toolkit is an open source plug-in for popular IDEs that uses the SAM CLI to build and deploy serverless applications on AWS. The AWS Toolkit also adds a simplified step-through debugging experience for Lambda function code. See the following links to get started.

* [CLion](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [GoLand](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [IntelliJ](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [WebStorm](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [Rider](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [PhpStorm](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [PyCharm](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [RubyMine](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [DataGrip](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [VS Code](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)
* [Visual Studio](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/welcome.html)

## 1. Deploy the Application

To deploy with a specific AWS profile:

```bash
sam build
sam deploy --profile your-aws-profile
```

For first-time deployment:

```bash
sam build
sam deploy --guided --profile your-aws-profile
```

The deployment will create:
- SQS Queue: `bach-messages-messages-queue`
- Lambda Function: `bach-messages-GetMessagesFunction-XXXXX`

After deployment, note the outputs:
- `MessagesQueueUrl`: URL of the SQS queue
- `GetMessagesFunction`: ARN of the Lambda function

## 2. Send Messages to SQS

Use the provided script to send 100 test messages:

```bash
cd scripts
python3 send_messages.py
```

The script will prompt for:
- **AWS Profile**: Your AWS profile name (or press Enter for default)
- **AWS Region**: AWS region (default: us-east-1)
- **SQS Queue URL**: The queue URL from deployment outputs

Example:
```
Enter AWS profile (or press Enter for default): my-profile
Enter AWS region (default: us-east-1): us-east-1
Enter SQS Queue URL: https://sqs.us-east-1.amazonaws.com/123456789012/bach-messages-messages-queue
```

## 3. Invoke Lambda Function

Invoke the Lambda function manually to process messages:

```bash
aws lambda invoke --function-name bach-messages-GetMessagesFunction-XXXXX --profile your-aws-profile response.json
```

Or using the full ARN:

```bash
aws lambda invoke --function-name arn:aws:lambda:us-east-1:123456789012:function:bach-messages-GetMessagesFunction-XXXXX --profile your-aws-profile response.json
```

The function will:
- Retrieve up to 10 messages from the SQS queue
- Process and delete the messages
- Return the processed message details in `response.json`

## Local Testing

Build and test locally:

```bash
sam build
sam local invoke GetMessagesFunction
```

Note: Local testing requires the SQS queue to be deployed and accessible.

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## View Lambda Logs

To view function logs:

```bash
sam logs -n GetMessagesFunction --stack-name "bach-messages" --tail --profile your-aws-profile
```

## Tests

Run tests:

```bash
pip install -r tests/requirements.txt --user
python -m pytest tests/unit -v
AWS_SAM_STACK_NAME="bach-messages" python -m pytest tests/integration -v
```

## Cleanup

To delete the application:

```bash
sam delete --stack-name "bach-messages" --profile your-aws-profile
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
