import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

# Store tokens in a JSON file (temporary solution)
# Ensure the file path is relative to where the services are running
if os.getenv('K_SERVICE'):
    TOKEN_FILE = '/tmp/user_tokens.json'
else:
    # Create the file in the services directory
    TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', 'user_tokens.json')
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)

def _read_tokens() -> Dict[str, Any]:
    """Read tokens from JSON file"""
    if not os.path.exists(TOKEN_FILE):
        return {}
    try:
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def _write_tokens(data: Dict[str, Any]):
    """Write tokens to JSON file"""
    # Ensure the file exists by creating it if needed
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(data, indent=2, fp=f)
    except FileNotFoundError:
        # Create the file and parent directory if they don't exist
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            json.dump(data, indent=2, fp=f)

def store_user_token(user_id: str, service_name: str, access_token: str, 
                     refresh_token: str = None, expires_at: str = None,
                     additional_data: Dict[str, Any] = None):
    """
    Store OAuth tokens for a user-service pair
    
    Args:
        user_id: User identifier (e.g., 'demo_user')
        service_name: Service name ('apollo', 'clay', 'hubspot')
        access_token: OAuth access token
        refresh_token: OAuth refresh token (optional)
        expires_at: Token expiry time in ISO format (optional)
        additional_data: Any extra data to store (e.g., user's email from service)
    """
    data = _read_tokens()
    
    # Create user entry if doesn't exist
    if user_id not in data:
        data[user_id] = {}
    
    # Store token data
    data[user_id][service_name] = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at,
        'connected_at': datetime.now().isoformat(),
        'additional_data': additional_data or {}
    }
    
    _write_tokens(data)
    print(f"✅ Stored {service_name} token for user {user_id}")

def get_user_token(user_id: str, service_name: str) -> Optional[str]:
    """
    Get OAuth access token for a user-service pair
    
    Args:
        user_id: User identifier
        service_name: Service name ('apollo', 'clay', 'hubspot')
    
    Returns:
        Access token string or None if not found
    """
    data = _read_tokens()
    
    if user_id not in data:
        return None
    
    if service_name not in data[user_id]:
        return None
    
    return data[user_id][service_name].get('access_token')

def get_user_token_data(user_id: str, service_name: str) -> Optional[Dict[str, Any]]:
    """
    Get full token data (including refresh token, expiry, etc.)
    
    Args:
        user_id: User identifier
        service_name: Service name
    
    Returns:
        Token data dict or None
    """
    data = _read_tokens()
    
    if user_id not in data:
        return None
    
    return data[user_id].get(service_name)

def is_service_connected(user_id: str, service_name: str) -> bool:
    """
    Check if user has connected a service
    
    Args:
        user_id: User identifier
        service_name: Service name
    
    Returns:
        True if connected, False otherwise
    """
    token = get_user_token(user_id, service_name)
    return token is not None

def disconnect_service(user_id: str, service_name: str):
    """
    Remove token for a user-service pair
    
    Args:
        user_id: User identifier
        service_name: Service name
    """
    data = _read_tokens()
    
    if user_id in data and service_name in data[user_id]:
        del data[user_id][service_name]
        _write_tokens(data)
        print(f"✅ Disconnected {service_name} for user {user_id}")

def get_all_connections(user_id: str) -> Dict[str, bool]:
    """
    Get connection status for all services
    
    Args:
        user_id: User identifier
    
    Returns:
        Dict with service names as keys and connection status as values
    """
    return {
        'apollo': is_service_connected(user_id, 'apollo'),
        'clay': is_service_connected(user_id, 'clay'),
        'hubspot': is_service_connected(user_id, 'hubspot')
    }


def get_api_key(user_id: str, service_name: str) -> Optional[str]:
    """
    Get API key for a user-service pair
    
    Args:
        user_id: User identifier
        service_name: Service name ('apollo', 'clay')
    
    Returns:
        API key string or None if not found
    """
    data = _read_tokens()
    
    if user_id not in data:
        return None
    
    key_name = f"{service_name}_api_key"
    return data[user_id].get(key_name)


def store_api_key(user_id: str, service_name: str, api_key: str):
    """
    Store API key for a user-service pair
    
    Args:
        user_id: User identifier
        service_name: Service name ('apollo', 'clay')
        api_key: API key to store
    """
    data = _read_tokens()
    
    if user_id not in data:
        data[user_id] = {}
    
    key_name = f"{service_name}_api_key"
    data[user_id][key_name] = api_key
    
    _write_tokens(data)
    print(f"✅ Stored {service_name} API key for user {user_id}")