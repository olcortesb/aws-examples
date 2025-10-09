import json
import os
import boto3


def lambda_handler(event, context):
    """Get batch of messages from SQS queue"""
    queue_url = os.environ.get('QUEUE_URL')
    
    if not queue_url:
        return {"error": "Queue URL not configured"}
    
    sqs = boto3.client('sqs')
    
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5
        )
        
        messages = response.get('Messages', [])
        processed_messages = []
        
        for msg in messages:
            processed_messages.append({
                "messageId": msg['MessageId'],
                "body": msg['Body'],
                "receiptHandle": msg['ReceiptHandle']
            })
            
            # Delete message after processing
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg['ReceiptHandle']
            )
        
        return {
            "queueUrl": queue_url,
            "messageCount": len(processed_messages),
            "messages": processed_messages
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
