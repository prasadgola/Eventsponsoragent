import json
import smtplib
import ssl
import os
import sys
import base64
from email.mime.text import MIMEText
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def parse_json_data(json_string: str) -> list:
    """
    Converts a JSON string into a Python list of dictionaries.
    This tool allows the agent to access structured data from another agent.
    """
    try:
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        # Handle cases where the input string is not valid JSON
        print(f"Error parsing JSON: {e}")
        return []


def format_outreach_email(sponsor_data: dict, your_name: str, your_company: str) -> dict:
    """
    Composes a friendly and personalized email from a dictionary of sponsor data.

    Args:
        sponsor_data (dict): A dictionary containing sponsor details (e.g., 'name', 'linkedin').
        your_name (str): Your name for the email signature.
        your_company (str): Your company name for the email signature.
        
    Returns:
        dict: A dictionary containing the formatted 'subject' and 'body' of the email.
    """
    # This is a basic example; the LLM would generate a more complex, personalized email.
    sponsor_name = sponsor_data.get("name", "Potential Sponsor")
    
    subject = f"Connecting about {sponsor_name}'s work"
    body = (
        f"Hello {sponsor_name},\n\n"
        "My name is {your_name} and I'm with {your_company}.\n\n"
        "I was impressed by your work on [mention a specific project or detail from their profile]."
        "I believe there's a great opportunity for us to collaborate on [mention a shared interest or project idea].\n\n"
        "Would you be open to a brief chat next week?\n\n"
        "Best regards,\n"
        "{your_name}\n"
        "{your_company}"
    )

    return {"subject": subject, "body": body}



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']



# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from config.settings import TOKEN_PATH

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_gmail_service():
    """Get Gmail service using token from secrets folder"""
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Token file not found at {TOKEN_PATH}")
    
    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH, 
        ['https://www.googleapis.com/auth/gmail.send']
    )
    
    return build('gmail', 'v1', credentials=creds)

def send_email_with_gmail_api(recipient: str, subject: str, body: str):
    """
    Sends an email using the Gmail API, handling authentication internally.
    
    Args:
        recipient (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The full body content of the email.
    
    Returns:
        str: A confirmation message.
    """
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