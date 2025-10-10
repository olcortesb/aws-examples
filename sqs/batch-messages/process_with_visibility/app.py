import json
import os
import boto3

def lambda_handler(event, context):
    """Process messages using visibility timeout - only delete messages that meet criteria"""
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
        skipped_messages = []
        
        for msg in messages:
            message_body = msg['Body']
            message_number = int(message_body)
            
            if message_number >= threshold:
                # Process and delete message
                processed_messages.append({
                    "messageId": msg['MessageId'],
                    "body": message_body,
                    "action": "processed_and_deleted"
                })
                
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=msg['ReceiptHandle']
                )
            else:
                # Skip message - let visibility timeout expire so it reappears
                skipped_messages.append({
                    "messageId": msg['MessageId'],
                    "body": message_body,
                    "action": "skipped_will_reappear"
                })
        
        return {
            "queueUrl": queue_url,
            "threshold": threshold,
            "totalMessages": len(messages),
            "processedCount": len(processed_messages),
            "skippedCount": len(skipped_messages),
            "processedMessages": processed_messages,
            "skippedMessages": skipped_messages
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}