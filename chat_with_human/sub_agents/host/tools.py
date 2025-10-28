"""
Host agent tools for event planning, sponsor outreach, and lead management.
All tools call the services backend via HTTP - no direct imports from services.
"""

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


# ============================================================================
# SPONSOR DATABASE TOOLS
# ============================================================================

def get_sponsors(category: str = "") -> str:
    """
    Get list of potential sponsors from database.
    
    Args:
        category: Optional category filter (e.g., "tech", "healthcare")
    
    Returns:
        JSON string of sponsors
    """
    params = {'category': category} if category else {}
    data = _call_service('GET', '/sponsors/list', params=params)
    return json.dumps(data)


# ============================================================================
# EMAIL TOOLS
# ============================================================================

def format_outreach_email(
    sponsor_name: str,
    sponsor_email: str,
    your_name: str,
    your_company: str,
    event_type: str
) -> str:
    """
    Format personalized outreach email with tracking.
    
    Args:
        sponsor_name: Name of the sponsor contact
        sponsor_email: Email address of sponsor
        your_name: Your name (event organizer)
        your_company: Your company/organization name
        event_type: Type of event (e.g., "tech conference")
    
    Returns:
        JSON string with subject, body, body_html, and tracking_id
    """
    result = _call_service('POST', '/email/format', json={
        'sponsor_name': sponsor_name,
        'sponsor_email': sponsor_email,
        'your_name': your_name,
        'your_company': your_company,
        'event_type': event_type
    })
    return json.dumps(result)


def send_email(
    recipient: str,
    subject: str,
    body: str,
    body_html: str = "",
    tracking_id: str = ""
) -> str:
    """
    Send email via Gmail with tracking.
    
    IMPORTANT: Use ALL fields from format_outreach_email output.
    
    Args:
        recipient: Recipient email address
        subject: Email subject line
        body: Plain text email body
        body_html: HTML version of email (with tracking pixel)
        tracking_id: Tracking ID for open detection
    
    Returns:
        Success message with tracking info
    """
    result = _call_service('POST', '/email/send', json={
        'recipient': recipient,
        'subject': subject,
        'body': body,
        'body_html': body_html,
        'tracking_id': tracking_id
    })
    return result.get('message', 'Email sent')


def get_email_stats(tracking_id: str = "") -> str:
    """
    Get email tracking statistics.
    
    Args:
        tracking_id: Specific tracking ID to check (optional)
    
    Returns:
        Tracking statistics as string
    """
    if tracking_id:
        result = _call_service('GET', f'/email/stats/{tracking_id}')
        return result.get('message', json.dumps(result))
    else:
        # Get overall stats (not implemented yet)
        return "Please provide a tracking_id to check specific email stats"


# ============================================================================
# UTILITY TOOLS
# ============================================================================

def parse_json(json_string: str) -> list:
    """
    Parse JSON string to Python object.
    
    Args:
        json_string: JSON string to parse
    
    Returns:
        Parsed Python list or dict
    """
    return json.loads(json_string)


# ============================================================================
# LEAD GENERATION TOOLS (NEW)
# ============================================================================

def find_sponsors_with_apollo(criteria: str, api_key: str) -> str:
    """
    Find sponsor leads using Apollo API.
    
    This tool searches for potential sponsor companies based on your criteria.
    The API key should be provided by the user in the conversation.
    
    Args:
        criteria: Search criteria (e.g., "tech companies in San Francisco")
        api_key: Apollo API key (provided by user in chat)
    
    Returns:
        JSON string of lead data with company names, domains, industries
    
    Example:
        User: "Find tech companies in SF"
        Agent calls: find_sponsors_with_apollo("tech companies in San Francisco", "user_api_key")
        Returns: [{"name": "TechCorp", "domain": "techcorp.com", ...}, ...]
    """
    try:
        result = _call_service('POST', '/leads/apollo/find-leads', json={
            'criteria': criteria,
            'api_key': api_key
        })
        return json.dumps(result)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Failed to find leads with Apollo. Check your API key."
        })


def enrich_leads_with_clay(leads_json: str, api_key: str) -> str:
    """
    Enrich lead data using Clay API.
    
    This tool adds contact information (emails, phone numbers, decision makers)
    to the leads you found with Apollo. The leads_json should be the result
    from find_sponsors_with_apollo that you stored in your memory.
    
    Args:
        leads_json: JSON string of leads from Apollo (from agent's memory)
        api_key: Clay API key (provided by user in chat)
    
    Returns:
        JSON string of enriched lead data with contact information
    
    Example:
        Agent has leads_json in memory: '[{"name": "TechCorp", ...}, ...]'
        Agent calls: enrich_leads_with_clay(leads_json, "user_api_key")
        Returns: [{"name": "TechCorp", "email": "contact@techcorp.com", ...}, ...]
    """
    try:
        result = _call_service('POST', '/leads/clay/enrich-leads', json={
            'leads_json': leads_json,
            'api_key': api_key
        })
        return json.dumps(result)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "message": "Failed to enrich leads with Clay. Check your API key."
        })


def upload_contacts_to_hubspot_json(contacts_json: str) -> str:
    """
    Upload contacts to HubSpot CRM.
    
    This tool syncs the enriched contacts to the user's HubSpot account.
    The user must have connected HubSpot in Settings first (OAuth flow).
    The contacts_json should be the enriched data from Clay that you stored
    in your memory.
    
    Args:
        contacts_json: JSON string of enriched contacts (from agent's memory)
    
    Returns:
        Success message with sync statistics
    
    Example:
        Agent has contacts_json in memory: '[{"name": "TechCorp", "email": "...", ...}, ...]'
        Agent calls: upload_contacts_to_hubspot_json(contacts_json)
        Returns: {"status": "success", "message": "Synced 5 contacts", ...}
    
    Note:
        This tool uses the HubSpot OAuth token that was saved when the user
        connected HubSpot in Settings. It does NOT require an API key to be
        passed in - the token is retrieved from persistent storage automatically.
    """
    try:
        result = _call_service('POST', '/leads/hubspot/sync-contacts', json={
            'contacts_json': contacts_json
        })
        return json.dumps(result)
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if "401" in error_msg or "not connected" in error_msg.lower():
            return json.dumps({
                "error": "HubSpot not connected",
                "message": "Please ask the user to connect HubSpot in Settings first. They need to click the hamburger menu → Settings → Connect HubSpot."
            })
        else:
            return json.dumps({
                "error": error_msg,
                "message": "Failed to sync contacts to HubSpot. Please try again or check the connection in Settings."
            })