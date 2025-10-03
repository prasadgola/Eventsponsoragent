import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_gmail_service():
    """Get Gmail API service"""
    
    # Try local path first, then cloud path
    token_paths = [
        './secrets/gmail_token.json',
        '../secrets/gmail_token.json',
        '/secrets/gmail_token.json',
        os.getenv('GMAIL_TOKEN_PATH', './secrets/gmail_token.json')
    ]
    
    token_path = None
    for path in token_paths:
        if os.path.exists(path):
            token_path = path
            break
    
    if not token_path:
        raise FileNotFoundError(f"Gmail token not found. Tried: {token_paths}")
    
    print(f"✅ Using Gmail token from: {token_path}")
    
    creds = Credentials.from_authorized_user_file(
        token_path,
        ['https://www.googleapis.com/auth/gmail.send']
    )
    
    return build('gmail', 'v1', credentials=creds)

def send_gmail_with_tracking(recipient: str, subject: str, body: str, body_html: str = ""):
    """Send email via Gmail API"""
    
    service = get_gmail_service()
    
    if body_html:
        # Multipart email with HTML
        message = MIMEMultipart('alternative')
        message['to'] = recipient
        message['from'] = 'me'
        message['subject'] = subject
        
        part1 = MIMEText(body, 'plain')
        part2 = MIMEText(body_html, 'html')
        
        message.attach(part1)
        message.attach(part2)
    else:
        # Plain text only
        message = MIMEText(body)
        message['to'] = recipient
        message['from'] = 'me'
        message['subject'] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    sent = service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()
    
    return sent['id']