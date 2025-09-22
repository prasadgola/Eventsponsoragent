import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# API Keys
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY', '')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID', '')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

# Gmail OAuth
GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID', '')
GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET', '')

# Paths
SECRETS_PATH = './secrets' if os.path.exists('./secrets') else '/secrets'
TOKEN_PATH = os.path.join(SECRETS_PATH, 'token.json')
CLIENT_SECRET_PATH = os.path.join(SECRETS_PATH, 'client_secret.json')

# Server Settings
PORT = int(os.getenv('PORT', 8000))
HOST = os.getenv('HOST', '0.0.0.0')