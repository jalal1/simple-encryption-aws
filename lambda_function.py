import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')
queue_url = 'https://sqs.[region].amazonaws.com/xxxxxxx/[queue_name].fifo'

def lambda_handler(event, context):
    print("event:", json.dumps(event))
    filename = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        print("File Name: " + filename)
        add_filename_to_SQS(filename)
        return filename
    except Exception as e:
        print(e)
        raise e
        
def add_filename_to_SQS(filename):
    sqs = boto3.client('sqs')
    sqs.send_message(QueueUrl=queue_url, MessageBody=filename, MessageGroupId='1')
    print('Done!')
