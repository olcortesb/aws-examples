#!/usr/bin/env python3
import boto3
import json
import sys

def send_messages():
    profile = input("Enter AWS profile (or press Enter for default): ").strip()
    region = input("Enter AWS region (default: us-east-1): ").strip() or 'us-east-1'
    
    if profile:
        session = boto3.Session(profile_name=profile)
        sqs = session.client('sqs', region_name=region)
    else:
        sqs = boto3.client('sqs', region_name=region)
    
    queue_url = input("Enter SQS Queue URL: ")
    
    for i in range(1, 101):
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=str(i)
        )
        print(f"Sent message: {i}")
    
    print("All 100 messages sent successfully!")

if __name__ == "__main__":
    send_messages()