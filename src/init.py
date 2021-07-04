import json
import boto3
import sys
from pprint import pprint

from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError

secret_name = "RingCredentials"
region_name = "ap-southeast-2"

def lambda_handler(event, context):
    init_ring()

def get_secret():
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
    ring_credentials = json.loads(get_secret())
    ring_credentials["token"] = json.dumps(token)
    ring_credentials["2fa"] = ""

    session = boto3.session.Session()
    client = session.client(
        service_name = "secretsmanager",
        region_name = region_name,
    )

    try:
        client.update_secret(
        SecretId = secret_name,
        SecretString = json.dumps(ring_credentials)
    )
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise    

def init_ring():
    ring_credentials = json.loads(get_secret())

    if ring_credentials["token"]:
        auth = Auth("ring-downloader", json.loads(ring_credentials["token"]), token_updated)
        auth.refresh_tokens()
    else:
        ring_credentials = json.loads(get_secret())
        username = ring_credentials["username"]
        password = ring_credentials["password"]
        auth = Auth("ring-downloader", None, token_updated)
        try:
            auth.fetch_token(username, password)
        except MissingTokenError:
            auth.fetch_token(username, password, ring_credentials["2fa"])

    ring = Ring(auth)
    ring.update_data()

    devices = ring.devices()
    pprint(f'Number of cams: {len(devices["stickup_cams"])}')
    
# if __name__ == "__main__":
#     init_ring()