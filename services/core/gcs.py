import os
import json
from google.cloud import storage

BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'event-sponsor-data')

def get_gcs_client():
    """Get GCS client"""
    return storage.Client()

def read_json_from_gcs(file_path: str):
    """Read JSON file from GCS"""
    
    try:
        client = get_gcs_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_path)
        
        if not blob.exists():
            return {}
        
        data = blob.download_as_text()
        return json.loads(data)
    except Exception as e:
        print(f"⚠️ GCS read error: {e}")
        return {}

def write_json_to_gcs(file_path: str, data: dict):
    """Write JSON file to GCS"""
    
    try:
        client = get_gcs_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_path)
        
        blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
    except Exception as e:
        print(f"❌ GCS write error: {e}")