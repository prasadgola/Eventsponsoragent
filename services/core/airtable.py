import os
import requests

def get_airtable_sponsors():
    """Get sponsors from Airtable"""
    
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    table_id = os.getenv('AIRTABLE_TABLE_ID')
    
    if not all([api_key, base_id, table_id]):
        print("⚠️ Airtable credentials not configured")
        return []
    
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        records = response.json().get("records", [])
        sponsors = [record.get("fields", {}) for record in records]
        
        return sponsors
    except Exception as e:
        print(f"❌ Airtable error: {e}")
        return []