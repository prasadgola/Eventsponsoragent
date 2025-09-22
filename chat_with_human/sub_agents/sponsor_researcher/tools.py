import requests
import json
import sys
import os

# Add parent directories to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from config.settings import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID

def call_airtable_api(name: str):
    """Retrieves all records from the Airtable sponsor database."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        records = response.json().get("records", [])
        clean_data = [record.get("fields", {}) for record in records]
        return json.dumps(clean_data)
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"API call failed: {e}"})