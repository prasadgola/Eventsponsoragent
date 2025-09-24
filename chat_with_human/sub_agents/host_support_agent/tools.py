# tools.py

import json
import base64
import os
import sys
import requests
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# This assumes your settings.py and token.json are configured correctly
# Add parent directories to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from config.settings import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID, TOKEN_PATH


# --- Airtable Tool ---
def call_airtable_api(name: str = ""):
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

# --- Utility Tool ---
def parse_json_data(json_string: str) -> list:
    """Converts a JSON string into a Python list of dictionaries."""
    try:
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []

# --- Email Tools ---
def format_outreach_email(sponsor_data: dict, your_name: str, your_company: str) -> dict:
    """Composes a friendly and personalized email from a dictionary of sponsor data."""
    sponsor_name = sponsor_data.get("name", "Potential Sponsor")
    
    subject = f"Connecting about {sponsor_name}'s work and a potential collaboration"
    body = (
        f"Hello {sponsor_name},\n\n"
        f"My name is {your_name} and I'm with {your_company}.\n\n"
        "I was impressed by your work and believe there may be an opportunity for us to collaborate on an exciting event we are planning.\n\n"
        "Would you be open to a brief chat next week?\n\n"
        f"Best regards,\n"
        f"{your_name}\n"
        f"{your_company}"
    )
    return {"subject": subject, "body": body}

def get_gmail_service():
    """Get Gmail service using token."""
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Token file not found at {TOKEN_PATH}")
    
    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH, 
        ['https://www.googleapis.com/auth/gmail.send']
    )
    return build('gmail', 'v1', credentials=creds)

def send_email_with_gmail_api(recipient: str, subject: str, body: str):
    """Sends an email using the Gmail API."""
    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message['to'] = recipient
        message['from'] = 'me'
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        sent_message = service.users().messages().send(
            userId='me', body={'raw': raw_message}).execute()
        return f"Email sent successfully to {recipient}. Message ID: {sent_message['id']}"
    except Exception as e:
        return f"Failed to send email to {recipient}. Error: {e}"