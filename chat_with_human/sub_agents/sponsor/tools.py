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

def find_events(event_type: str = "", location: str = "") -> str:
    """
    Search for upcoming events.
    
    Args:
        event_type: Type of event (e.g., "tech", "healthcare")
        location: Location preference
    
    Returns:
        JSON string of events
    """
    params = {}
    if event_type:
        params['type'] = event_type
    if location:
        params['location'] = location
    
    data = _call_service('GET', '/events/search', params=params)
    return json.dumps(data)

def register_for_event(event_id: str, user_name: str, user_email: str) -> str:
    """
    Register user for an event.
    
    Args:
        event_id: ID of the event
        user_name: Attendee's name
        user_email: Attendee's email
    
    Returns:
        Confirmation message
    """
    result = _call_service('POST', '/events/register', json={
        'event_id': event_id,
        'user_name': user_name,
        'user_email': user_email
    })
    return result.get('message', 'Registration successful')

def find_sponsor_opportunities(industry: str = "", budget: str = "") -> str:
    """
    Find events seeking sponsorship.
    
    Args:
        industry: Industry preference
        budget: Budget range (e.g., "$5k-$10k")
    
    Returns:
        JSON string of sponsorship opportunities
    """
    params = {}
    if industry:
        params['industry'] = industry
    if budget:
        params['budget'] = budget
    
    data = _call_service('GET', '/sponsors/opportunities', params=params)
    return json.dumps(data)

def parse_json(json_string: str) -> list:
    """Parse JSON string to Python object"""
    return json.loads(json_string)