import requests
import json
import os

SERVICES_URL = os.getenv('SERVICES_URL', 'http://localhost:8001')

def _call_service(method: str, endpoint: str, **kwargs):
    """Helper to call Services Server"""
    url = f"{SERVICES_URL}{endpoint}"
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response.json()

def get_sponsors() -> str:
    """
    Get all sponsors from database.
    
    Returns:
        JSON string of all sponsor data
    """
    data = _call_service('GET', '/sponsors/list')
    return json.dumps(data)

def format_outreach_email(sponsor_name: str, sponsor_email: str, 
                          your_name: str, your_company: str, event_type: str) -> dict:
    """
    Format a personalized outreach email with tracking.
    
    Args:
        sponsor_name: Name of the sponsor
        sponsor_email: Sponsor's email address
        your_name: User's name
        your_company: User's company/organization
        event_type: Type of event being hosted
    
    Returns:
        Dict with subject, body, body_html, tracking_id
    """
    return _call_service('POST', '/email/format', json={
        'sponsor_name': sponsor_name,
        'sponsor_email': sponsor_email,
        'your_name': your_name,
        'your_company': your_company,
        'event_type': event_type
    })

def send_email(recipient: str, subject: str, body: str, 
               body_html: str = "", tracking_id: str = "") -> str:
    """
    Send email via Gmail with optional tracking.
    
    Args:
        recipient: Email recipient
        subject: Email subject
        body: Plain text body
        body_html: HTML body (optional, for tracking)
        tracking_id: Tracking ID (optional)
    
    Returns:
        Success message with tracking info
    """
    try:
        result = _call_service('POST', '/email/send', json={
            'recipient': recipient,
            'subject': subject,
            'body': body,
            'body_html': body_html,
            'tracking_id': tracking_id
        })
        return result.get('message', 'Email sent successfully')
    except Exception as e:
        # Return a user-friendly error message
        return f"Sorry, there was an error sending the email: {e}"

def get_email_stats(tracking_id: str = "") -> str:
    """
    Get email tracking statistics to see if sponsors opened emails.
    
    Args:
        tracking_id: Specific email tracking ID (optional). 
                     Leave empty to get overall campaign stats.
    
    Returns:
        Human-readable message about email opens and engagement.
    
    Use this when user asks:
    - "Show me email statistics"
    - "Did anyone open my emails?"
    - "How many sponsors opened?"
    - "Check tracking for [id]"
    """
    endpoint = f'/email/stats/{tracking_id}' if tracking_id else '/email/stats'
    result = _call_service('GET', endpoint)
    
    # Debug: print what we got
    print(f"DEBUG: API result = {result}")
    message = result.get('message', '')
    print(f"DEBUG: Extracted message = {message}")
    
    return message

def parse_json(json_string: str) -> list:
    """
    Parse JSON string to Python list.
    
    Args:
        json_string: JSON formatted string
    
    Returns:
        Parsed list/dict
    """
    return json.loads(json_string)