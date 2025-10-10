import json
import os
import boto3

def lambda_handler(event, context):
    """Process messages and send failed ones to DLQ"""
    queue_url = os.environ.get('QUEUE_URL')
    dlq_url = os.environ.get('DLQ_URL')
    threshold = int(os.environ.get('THRESHOLD', '50'))
    
    if not queue_url or not dlq_url:
        return {"error": "Queue URLs not configured"}
    
    sqs = boto3.client('sqs')
    
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5
        )
        
        messages = response.get('Messages', [])
        processed_messages = []
        dlq_messages = []
        
        for msg in messages:
            message_body = msg['Body']
            message_number = int(message_body)
            
            if message_number >= threshold:
                processed_messages.append({
                    "messageId": msg['MessageId'],
                    "body": message_body,
                    "action": "processed"
                })
            else:
                # Send to DLQ
                sqs.send_message(
                    QueueUrl=dlq_url,
                    MessageBody=message_body
                )
                dlq_messages.append({
                    "messageId": msg['MessageId'],
                    "body": message_body,
                    "action": "sent_to_dlq"
                })
            
            # Delete from original queue
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg['ReceiptHandle']
            )
        
        return {
            "queueUrl": queue_url,
            "dlqUrl": dlq_url,
            "threshold": threshold,
            "totalMessages": len(messages),
            "processedCount": len(processed_messages),
            "dlqCount": len(dlq_messages),
            "processedMessages": processed_messages,
            "dlqMessages": dlq_messages
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}