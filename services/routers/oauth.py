from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from typing import Optional
from core.token_store import (
    store_user_token, 
    get_all_connections,
    disconnect_service,
    is_service_connected
)

router = APIRouter()

# OAuth Configuration
# You'll need to set these in your .env file after registering apps
APOLLO_CLIENT_ID = os.getenv('APOLLO_CLIENT_ID', '')
APOLLO_CLIENT_SECRET = os.getenv('APOLLO_CLIENT_SECRET', '')
APOLLO_REDIRECT_URI = os.getenv('APOLLO_REDIRECT_URI', 'http://localhost:8001/oauth/apollo/callback')

CLAY_CLIENT_ID = os.getenv('CLAY_CLIENT_ID', '')
CLAY_CLIENT_SECRET = os.getenv('CLAY_CLIENT_SECRET', '')
CLAY_REDIRECT_URI = os.getenv('CLAY_REDIRECT_URI', 'http://localhost:8001/oauth/clay/callback')

HUBSPOT_CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID', '')
HUBSPOT_CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET', '')
HUBSPOT_REDIRECT_URI = os.getenv('HUBSPOT_REDIRECT_URI', 'http://localhost:8001/oauth/hubspot/callback')

# For now, hardcode the demo user
DEMO_USER_ID = 'demo_user'

# Frontend URL for redirects after OAuth
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:8080')


# ============================================================================
# APOLLO OAUTH
# ============================================================================

@router.get("/apollo/authorize")
async def apollo_authorize(user_id: str = Query(default=DEMO_USER_ID)):
    """
    Step 1: Redirect user to Apollo OAuth page
    """
    if not APOLLO_CLIENT_ID:
        raise HTTPException(
            status_code=500, 
            detail="Apollo OAuth not configured. Set APOLLO_CLIENT_ID in .env"
        )
    
    # Build Apollo authorization URL
    # Note: Update this URL based on Apollo's actual OAuth endpoint
    auth_url = (
        f"https://app.apollo.io/oauth/authorize?"
        f"client_id={APOLLO_CLIENT_ID}&"
        f"redirect_uri={APOLLO_REDIRECT_URI}&"
        f"response_type=code&"
        f"state={user_id}"  # Pass user_id in state to get it back
    )
    
    print(f"🔵 Redirecting {user_id} to Apollo OAuth...")
    return RedirectResponse(url=auth_url)


@router.get("/apollo/callback")
async def apollo_callback(
    code: str = Query(...),
    state: str = Query(default=DEMO_USER_ID)
):
    """
    Step 2: Apollo redirects back here with authorization code
    Exchange code for access token
    """
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")
    
    user_id = state  # Get user_id from state parameter
    
    try:
        # Exchange authorization code for access token
        # Note: Update token URL based on Apollo's actual endpoint
        token_response = requests.post(
            'https://app.apollo.io/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': APOLLO_REDIRECT_URI,
                'client_id': APOLLO_CLIENT_ID,
                'client_secret': APOLLO_CLIENT_SECRET
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get Apollo token: {token_response.text}"
            )
        
        token_data = token_response.json()
        
        # Store tokens
        store_user_token(
            user_id=user_id,
            service_name='apollo',
            access_token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            expires_at=token_data.get('expires_at'),
            additional_data={
                'token_type': token_data.get('token_type'),
                'scope': token_data.get('scope')
            }
        )
        
        print(f"✅ Apollo connected for {user_id}")
        
        # Redirect back to frontend with success message
        return RedirectResponse(
            url=f"{FRONTEND_URL}?oauth_success=apollo"
        )
        
    except Exception as e:
        print(f"❌ Apollo OAuth error: {e}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}?oauth_error=apollo&message={str(e)}"
        )


# ============================================================================
# CLAY OAUTH
# ============================================================================

@router.get("/clay/authorize")
async def clay_authorize(user_id: str = Query(default=DEMO_USER_ID)):
    """
    Step 1: Redirect user to Clay OAuth page
    """
    if not CLAY_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Clay OAuth not configured. Set CLAY_CLIENT_ID in .env"
        )
    
    # Build Clay authorization URL
    # Note: Update based on Clay's actual OAuth endpoint
    auth_url = (
        f"https://app.clay.com/oauth/authorize?"
        f"client_id={CLAY_CLIENT_ID}&"
        f"redirect_uri={CLAY_REDIRECT_URI}&"
        f"response_type=code&"
        f"state={user_id}"
    )
    
    print(f"🟣 Redirecting {user_id} to Clay OAuth...")
    return RedirectResponse(url=auth_url)


@router.get("/clay/callback")
async def clay_callback(
    code: str = Query(...),
    state: str = Query(default=DEMO_USER_ID)
):
    """
    Step 2: Clay redirects back here with authorization code
    """
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")
    
    user_id = state
    
    try:
        # Exchange code for token
        # Note: Update based on Clay's actual token endpoint
        token_response = requests.post(
            'https://app.clay.com/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': CLAY_REDIRECT_URI,
                'client_id': CLAY_CLIENT_ID,
                'client_secret': CLAY_CLIENT_SECRET
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get Clay token: {token_response.text}"
            )
        
        token_data = token_response.json()
        
        store_user_token(
            user_id=user_id,
            service_name='clay',
            access_token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            expires_at=token_data.get('expires_at'),
            additional_data={
                'token_type': token_data.get('token_type'),
                'scope': token_data.get('scope')
            }
        )
        
        print(f"✅ Clay connected for {user_id}")
        
        return RedirectResponse(
            url=f"{FRONTEND_URL}?oauth_success=clay"
        )
        
    except Exception as e:
        print(f"❌ Clay OAuth error: {e}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}?oauth_error=clay&message={str(e)}"
        )


# ============================================================================
# HUBSPOT OAUTH
# ============================================================================

@router.get("/hubspot/authorize")
async def hubspot_authorize(user_id: str = Query(default=DEMO_USER_ID)):
    """
    Step 1: Redirect user to HubSpot OAuth page
    """
    if not HUBSPOT_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="HubSpot OAuth not configured. Set HUBSPOT_CLIENT_ID in .env"
        )
    
    # HubSpot OAuth URL (this one is accurate)
    auth_url = (
        f"https://app.hubspot.com/oauth/authorize?"
        f"client_id={HUBSPOT_CLIENT_ID}&"
        f"redirect_uri={HUBSPOT_REDIRECT_URI}&"
        f"scope=crm.objects.contacts.write%20crm.objects.contacts.read%20crm.schemas.contacts.read"
        f"&state={user_id}"
    )
    
    print(f"🟠 Redirecting {user_id} to HubSpot OAuth...")
    return RedirectResponse(url=auth_url)


@router.get("/hubspot/callback")
async def hubspot_callback(
    code: str = Query(...),
    state: str = Query(default=DEMO_USER_ID)
):
    """
    Step 2: HubSpot redirects back here with authorization code
    """
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided")
    
    user_id = state
    
    try:
        # Exchange code for token (HubSpot's actual endpoint)
        token_response = requests.post(
            'https://api.hubapi.com/oauth/v1/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': HUBSPOT_REDIRECT_URI,
                'client_id': HUBSPOT_CLIENT_ID,
                'client_secret': HUBSPOT_CLIENT_SECRET
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get HubSpot token: {token_response.text}"
            )
        
        token_data = token_response.json()
        
        store_user_token(
            user_id=user_id,
            service_name='hubspot',
            access_token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            expires_at=token_data.get('expires_in'),  # HubSpot uses expires_in (seconds)
            additional_data={
                'token_type': token_data.get('token_type'),
                'hub_id': token_data.get('hub_id')
            }
        )
        
        print(f"✅ HubSpot connected for {user_id}")
        
        return RedirectResponse(
            url=f"{FRONTEND_URL}?oauth_success=hubspot"
        )
        
    except Exception as e:
        print(f"❌ HubSpot OAuth error: {e}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}?oauth_error=hubspot&message={str(e)}"
        )


# ============================================================================
# STATUS & MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/status")
async def get_oauth_status(user_id: str = Query(default=DEMO_USER_ID)):
    """
    Get connection status for all services
    """
    connections = get_all_connections(user_id)
    
    return {
        "user_id": user_id,
        "connections": connections,
        "services": {
            "apollo": {
                "connected": connections['apollo'],
                "name": "Apollo",
                "description": "Find sponsor leads"
            },
            "clay": {
                "connected": connections['clay'],
                "name": "Clay",
                "description": "Enrich lead data"
            },
            "hubspot": {
                "connected": connections['hubspot'],
                "name": "HubSpot",
                "description": "Manage contacts and campaigns"
            }
        }
    }


@router.post("/disconnect/{service_name}")
async def disconnect_oauth_service(
    service_name: str,
    user_id: str = Query(default=DEMO_USER_ID)
):
    """
    Disconnect a service for a user
    """
    if service_name not in ['apollo', 'clay', 'hubspot']:
        raise HTTPException(status_code=400, detail=f"Unknown service: {service_name}")
    
    if not is_service_connected(user_id, service_name):
        raise HTTPException(status_code=404, detail=f"{service_name} is not connected")
    
    disconnect_service(user_id, service_name)
    
    return {
        "success": True,
        "message": f"Disconnected {service_name}",
        "service": service_name,
        "user_id": user_id
    }


# ============================================================================
# API KEY MANAGEMENT ENDPOINTS
# ============================================================================

class ApiKeysRequest(BaseModel):
    user_id: str
    apollo_api_key: Optional[str] = None
    clay_api_key: Optional[str] = None

@router.get("/api-keys")
async def get_api_keys(user_id: str = Query(default=DEMO_USER_ID)):
    """
    Get stored API keys for a user (for settings page)
    """
    from core.token_store import _read_tokens
    
    data = _read_tokens()
    user_data = data.get(user_id, {})
    
    return {
        "user_id": user_id,
        "apollo_api_key": user_data.get("apollo_api_key", ""),
        "clay_api_key": user_data.get("clay_api_key", "")
    }


@router.post("/api-keys")
async def save_api_keys(request: ApiKeysRequest):
    """
    Save API keys for a user
    """
    from core.token_store import _read_tokens, _write_tokens
    
    user_id = request.user_id
    
    # Read existing data
    data = _read_tokens()
    
    # Create user entry if doesn't exist
    if user_id not in data:
        data[user_id] = {}
    
    # Store API keys (only if provided and not empty)
    if request.apollo_api_key and request.apollo_api_key.strip():
        data[user_id]['apollo_api_key'] = request.apollo_api_key.strip()
    
    if request.clay_api_key and request.clay_api_key.strip():
        data[user_id]['clay_api_key'] = request.clay_api_key.strip()
    
    # Write back to file
    _write_tokens(data)
    
    print(f"✅ Saved API keys for user {user_id}")
    
    return {
        "success": True,
        "message": "API keys saved successfully",
        "user_id": user_id
    }