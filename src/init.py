import json
import boto3
from botocore.exceptions import ClientError
import sys

def lambda_handler(event, context):
    secret_data = get_secret()
    return {
        'statusCode': 200,
        'body': json.dumps(f'Hello {event["name"]}!')
    }

def get_secret():
    secret_name = "RingCredentials"
    region_name = "ap-southeast-2"

    session = boto3.session.Session()
    client = session.client(
        service_name = 'secretsmanager',
        region_name = region_name,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    else:
        text_secret_data = get_secret_value_response['SecretString']
        return text_secret_data
    
    