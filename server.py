import boto3
import logging
from botocore.exceptions import ClientError
import os
import time
import configparser
# Server.py will be runing on AWS EC2 instance in order to encrypt files using OPENSSL
# Steps:
#   - Check if the queue is not empty and then pop a message
#   - Get filename from the message and download the file from S3 bucket
#   - Encrypt the file, and save the output file to S3 output bucket
#   - Clean processed files from EC2.


queue_url = 'https://sqs.[region].amazonaws.com/xxxxxxx/[queue_name].fifo' # Not used below. get from aws SQS if needed.
queue_name = '[queue_name].fifo' # get from aws SQS

config = configparser.RawConfigParser()
config.read('credentials')
user_access_key_id = config.get('default', 'aws_access_key_id')
user_secret_access_key = config.get('default', 'aws_secret_access_key')
aws_session_token = config.get('default', 'aws_session_token')

bucket_name = "[bucket_name]"
output_bucket_name = "[output_bucket_name]"

s3_client = boto3.client('s3',
                        aws_access_key_id=user_access_key_id,
                        aws_secret_access_key=user_secret_access_key,
                        aws_session_token = aws_session_token,
                        region_name = 'us-east-1'
                        )

sqs = boto3.resource(
    "sqs",
    aws_access_key_id=user_access_key_id,
    aws_secret_access_key=user_secret_access_key,
    aws_session_token=aws_session_token,
    region_name = 'us-east-1'
)

if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # get a message from the queue
    queue = sqs.get_queue_by_name(QueueName=queue_name)

    while(True):
        try:
            for message in queue.receive_messages():
                # Print out the body of the message
                file_name = message.body
                print("======> New file name: ", file_name)
                # Let the queue know that the message is processed
                message.delete()

                # get file from S3
                s3_client.download_file(bucket_name, file_name, file_name)

                # encrypt file
                if '.' in file_name:
                    encrypted_file_name = file_name.split(".")[0] + "_enc" +"."+file_name.split(".")[1]
                else:
                    encrypted_file_name = file_name + "_enc"

                # encrypted_file_name = file_name.split(".")[0] + "_enc" +"."+file_name.split(".")[1]
                command = "openssl aes-256-cbc -a -salt -pass pass:'000' -in "+ file_name+ " -out "+ encrypted_file_name
                os.system(command)

                # save encrypted file to S3
                s3_client.upload_file(encrypted_file_name, output_bucket_name, encrypted_file_name)

                # delete files from local machine
                os.remove(file_name)
                os.remove(encrypted_file_name)

                print("File encrypted successfully!")

        except Exception as e:
            print(e)

        print("Sleeping...")
        time.sleep(2) # 2 seconds


