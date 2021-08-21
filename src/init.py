import json
import logging
import boto3
import sys
import os

from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError

secret_name = os.environ.get("CREDENTIALS_SECRET_NAME")
bucket_name = os.environ.get("BUCKET_NAME")
video_history_limit = os.environ.get("VIDEO_HISTORY_LIMIT")
topic_arn = os.environ.get("TOPIC_ARN")
directory_prefix = "/tmp/"
region_name = "ap-southeast-2"

logger = logging.getLogger()

def lambda_handler(event, context):
    setLogger()
    ring = init_ring()
    upload_recent_videos(ring)

def setLogger():
    stdout_handler = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.INFO)
    logger.addHandler(stdout_handler)

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

    return ring

def upload_recent_videos(ring: Ring):
    devices = ring.devices()
    
    front_cam = devices["stickup_cams"][0]
    back_cam = devices["stickup_cams"][1]
    
    upload_video(front_cam, "front_cam")
    upload_video(back_cam, "back_cam")

def upload_video(cam, cam_name):
    history = cam.history(limit = video_history_limit)

    logger.info(f"No. of videos to upload for {cam_name}: {len(history)}")

    s3_client = boto3.client("s3")
    sns_client = boto3.client("sns")

    for event in history:
        file_name = f"{event['id']}_{cam_name}.mp4"
        
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f"{event['id']}", MaxKeys=1)
        obj = response.get('Contents', [])
        if (len(obj) > 0):
            logger.info(f"file: {file_name} exists, skipping.")
        else:
            local_file_path = f"{directory_prefix}{file_name}"
            cam.recording_download(event['id'], local_file_path)
            logger.info(f"Uploading {bucket_name}/{file_name}")
            response = s3_client.upload_file(local_file_path, bucket_name, file_name)
            message = { "bucket_name": bucket_name, "file_name": file_name, "cam_name": cam_name }
            sns_client.publish( 
                TopicArn = topic_arn,
                MessageStructure = "json",
                Message = json.dumps({"default": json.dumps(message)})
            )

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
        logger.error("Unexpected error:", sys.exc_info()[0])
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
        logger.error("Unexpected error:", sys.exc_info()[0])
        raise    

# if __name__ == "__main__":
#     lambda_handler(None, None)