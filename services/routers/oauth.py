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
HUBSPOT_CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID') or os.getenv('HUBSPOT_CLIENT_SECRET')  # Try both env names
HUBSPOT_CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET')

# Detect environment
is_cloud_run = os.getenv('K_SERVICE') is not None

# Configure URLs based on environment
if is_cloud_run:
    # Production: Use Cloud Run URLs
    SERVICES_BASE_URL = os.getenv('SERVICES_URL') or 'https://services-backend-766291037876.us-central1.run.app'
    FRONTEND_URL = 'https://storage.googleapis.com/event-sponsor-frontend/index.html'
else:
    # Local development
    SERVICES_BASE_URL = os.getenv('SERVICES_URL') or 'http://localhost:8001'
    FRONTEND_URL = os.getenv('FRONTEND_URL') or 'http://localhost:8080'

HUBSPOT_REDIRECT_URI = f"{SERVICES_BASE_URL}/oauth/hubspot/callback"

# For now, hardcode the demo user
DEMO_USER_ID = 'demo_user'

print(f"🔧 OAuth Configuration:")
print(f"   Environment: {'Cloud Run' if is_cloud_run else 'Local'}")
print(f"   Services URL: {SERVICES_BASE_URL}")
print(f"   Frontend URL: {FRONTEND_URL}")
print(f"   HubSpot Redirect URI: {HUBSPOT_REDIRECT_URI}")
print(f"   HubSpot Client ID configured: {bool(HUBSPOT_CLIENT_ID)}")


# ============================================================================
# HUBSPOT OAUTH
# ============================================================================

@router.get("/hubspot/authorize")
async def hubspot_authorize(user_id: str = Query(default=DEMO_USER_ID)):
    """
    Step 1: Redirect user to HubSpot OAuth page
    """
    if not HUBSPOT_CLIENT_ID or not HUBSPOT_CLIENT_SECRET:
        print(f"❌ HubSpot OAuth not configured!")
        print(f"   HUBSPOT_CLIENT_ID: {bool(HUBSPOT_CLIENT_ID)}")
        print(f"   HUBSPOT_CLIENT_SECRET: {bool(HUBSPOT_CLIENT_SECRET)}")
        raise HTTPException(
            status_code=500,
            detail="HubSpot OAuth not configured. Set HUBSPOT_CLIENT_ID and HUBSPOT_CLIENT_SECRET in environment variables or Secret Manager"
        )
    
    # HubSpot OAuth URL with required scopes
    auth_url = (
        f"https://app.hubspot.com/oauth/authorize?"
        f"client_id={HUBSPOT_CLIENT_ID}&"
        f"redirect_uri={HUBSPOT_REDIRECT_URI}&"
        f"scope=crm.objects.contacts.write%20crm.objects.contacts.read%20crm.schemas.contacts.read%20crm.objects.companies.write"
        f"&state={user_id}"
    )
    
    print(f"🟠 Redirecting {user_id} to HubSpot OAuth...")
    print(f"   Redirect URI: {HUBSPOT_REDIRECT_URI}")
    print(f"   Frontend will redirect to: {FRONTEND_URL}")
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
    Note: Apollo and Clay use API keys stored in localStorage on frontend
    """
    connections = get_all_connections(user_id)
    
    return {
        "user_id": user_id,
        "connections": connections,
        "services": {
            "apollo": {
                "connected": False,  # API key stored in frontend
                "name": "Apollo",
                "description": "Find sponsor leads (API key required)",
                "auth_method": "api_key"
            },
            "clay": {
                "connected": False,  # API key stored in frontend
                "name": "Clay",
                "description": "Enrich lead data (API key required)",
                "auth_method": "api_key"
            },
            "hubspot": {
                "connected": connections['hubspot'],
                "name": "HubSpot",
                "description": "Manage contacts and campaigns",
                "auth_method": "oauth"
            }
        }
    }


@router.post("/disconnect/{service_name}")
async def disconnect_oauth_service(
    service_name: str,
    user_id: str = Query(default=DEMO_USER_ID)
):
    """
    Disconnect a service for a user (only works for OAuth services like HubSpot)
    """
    if service_name not in ['hubspot']:
        raise HTTPException(
            status_code=400, 
            detail=f"Service {service_name} uses API keys, not OAuth. Manage keys in Settings."
        )
    
    if not is_service_connected(user_id, service_name):
        raise HTTPException(status_code=404, detail=f"{service_name} is not connected")
    
    disconnect_service(user_id, service_name)
    
    return {
        "success": True,
        "message": f"Disconnected {service_name}",
        "service": service_name,
        "user_id": user_id
    }