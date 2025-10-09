import json
import os
import boto3

def lambda_handler(event, context):
    """Process messages and return to queue if number is less than threshold"""
    queue_url = os.environ.get('QUEUE_URL')
    threshold = int(os.environ.get('THRESHOLD', '50'))
    
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
        returned_messages = []
        
        for msg in messages:
            message_body = msg['Body']
            message_number = int(message_body)
            
            if message_number < threshold:
                # Return message to queue
                sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=message_body
                )
                returned_messages.append({
                    "messageId": msg['MessageId'],
                    "body": message_body,
                    "action": "returned_to_queue"
                })
            else:
                processed_messages.append({
                    "messageId": msg['MessageId'],
                    "body": message_body,
                    "action": "processed"
                })
            
            # Delete original message
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg['ReceiptHandle']
            )
        
        return {
            "queueUrl": queue_url,
            "threshold": threshold,
            "totalMessages": len(messages),
            "processedCount": len(processed_messages),
            "returnedCount": len(returned_messages),
            "processedMessages": processed_messages,
            "returnedMessages": returned_messages
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}