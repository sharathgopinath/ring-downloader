import json
import boto3
import sys
from pathlib import Path
from pprint import pprint

from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError

cache_file = Path("token.cache")

def lambda_handler(event, context):
    # init_ring()
    return {
        'statusCode': 200,
        'body': json.dumps(f'Hello {event["name"]}!')
    }

def get_secret():
    secret_name = "RingCredentials"
    region_name = "ap-southeast-2"

    session = boto3.session.Session()
    client = session.client(
        service_name = "secretsmanager",
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
        text_secret_data = get_secret_value_response["SecretString"]
        return text_secret_data

def token_updated(token):
    cache_file.write_text(json.dumps(token))

def init_ring():
    if cache_file.is_file():
        auth = Auth("ring-downloader", json.loads(cache_file.read_text()), token_updated)
        auth.refresh_tokens()
    else:
        ring_credentials = json.loads(get_secret())
        username = ring_credentials["username"]
        password = ring_credentials["password"]
        auth = Auth("ring-downloader", None, token_updated)
        try:
            auth.fetch_token(username, password)
        except MissingTokenError:
            auth.fetch_token(username, password, ring_credentials["token"])

    ring = Ring(auth)
    ring.update_data()

    devices = ring.devices()
    pprint(f'Number of cams: {len(devices["stickup_cams"])}')
    
# if __name__ == "__main__":
#     init_ring()