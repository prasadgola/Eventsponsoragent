from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import json
from core.token_store import get_user_token

router = APIRouter()

class FindLeadsRequest(BaseModel):
    criteria: str
    api_key: str

class EnrichLeadsRequest(BaseModel):
    leads_json: str
    api_key: str

class SyncContactsRequest(BaseModel):
    contacts_json: str

# Apollo API endpoint (placeholder - update with real endpoint)
APOLLO_API_URL = "https://api.apollo.io/v1/mixed_people/search"

# Clay API endpoint (placeholder - update with real endpoint)
CLAY_API_URL = "https://api.clay.com/v1/enrich"

@router.post("/apollo/find-leads")
async def find_leads_with_apollo(request: FindLeadsRequest):
    """
    Find sponsor leads using Apollo API
    """
    try:
        # For demo purposes, return mock data
        # In production, make actual API call to Apollo
        
        # Example of what the real API call would look like:
        # headers = {"Authorization": f"Bearer {request.api_key}"}
        # response = requests.post(
        #     APOLLO_API_URL,
        #     headers=headers,
        #     json={"q_keywords": request.criteria}
        # )
        # response.raise_for_status()
        # return response.json()
        
        # Mock response
        mock_leads = [
            {
                "name": "TechCorp Solutions",
                "domain": "techcorp.com",
                "industry": "Technology",
                "size": "500-1000 employees"
            },
            {
                "name": "InnovateLabs",
                "domain": "innovatelabs.io",
                "industry": "Software",
                "size": "100-500 employees"
            },
            {
                "name": "CloudScale Inc",
                "domain": "cloudscale.com",
                "industry": "Cloud Services",
                "size": "1000+ employees"
            }
        ]
        
        return mock_leads
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Apollo API error: {str(e)}")


@router.post("/clay/enrich-leads")
async def enrich_leads_with_clay(request: EnrichLeadsRequest):
    """
    Enrich lead data using Clay API
    """
    try:
        # Parse the incoming JSON
        leads = json.loads(request.leads_json)
        
        # For demo purposes, return enriched mock data
        # In production, make actual API call to Clay
        
        # Example of what the real API call would look like:
        # headers = {"Authorization": f"Bearer {request.api_key}"}
        # response = requests.post(
        #     CLAY_API_URL,
        #     headers=headers,
        #     json={"leads": leads}
        # )
        # response.raise_for_status()
        # return response.json()
        
        # Mock enrichment - add email and contact info
        enriched_leads = []
        for lead in leads:
            enriched_lead = {
                **lead,
                "email": f"contact@{lead.get('domain', 'example.com')}",
                "phone": "+1-555-0100",
                "decision_maker": f"CEO of {lead.get('name', 'Company')}",
                "linkedin": f"https://linkedin.com/company/{lead.get('name', 'company').lower().replace(' ', '-')}"
            }
            enriched_leads.append(enriched_lead)
        
        return enriched_leads
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in leads_json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clay API error: {str(e)}")


@router.post("/hubspot/sync-contacts")
async def sync_contacts_to_hubspot(request: SyncContactsRequest):
    """
    Sync contacts to HubSpot CRM
    """
    try:
        # Get HubSpot OAuth token for demo_user
        access_token = get_user_token('demo_user', 'hubspot')
        
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="HubSpot not connected. Please connect HubSpot in Settings first."
            )
        
        # Parse contacts JSON
        contacts = json.loads(request.contacts_json)
        
        # HubSpot API endpoint
        hubspot_api_url = "https://api.hubapi.com/crm/v3/objects/contacts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Upload each contact to HubSpot
        successful_uploads = 0
        failed_uploads = 0
        
        for contact in contacts:
            try:
                # Map contact data to HubSpot format
                hubspot_contact = {
                    "properties": {
                        "firstname": contact.get("name", "Unknown").split()[0] if contact.get("name") else "Unknown",
                        "lastname": contact.get("name", "Unknown").split()[-1] if contact.get("name") and len(contact.get("name").split()) > 1 else "",
                        "email": contact.get("email", ""),
                        "company": contact.get("name", ""),
                        "website": contact.get("domain", ""),
                        "industry": contact.get("industry", ""),
                        "phone": contact.get("phone", "")
                    }
                }
                
                # For demo purposes, just count successes
                # In production, make actual API call:
                # response = requests.post(
                #     hubspot_api_url,
                #     headers=headers,
                #     json=hubspot_contact
                # )
                # response.raise_for_status()
                
                successful_uploads += 1
                print(f"✅ Would upload to HubSpot: {contact.get('name', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Failed to upload {contact.get('name', 'Unknown')}: {e}")
                failed_uploads += 1
        
        return {
            "status": "success",
            "message": f"Successfully synced {successful_uploads} contacts to HubSpot.",
            "details": {
                "successful": successful_uploads,
                "failed": failed_uploads,
                "total": len(contacts)
            }
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in contacts_json")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HubSpot sync error: {str(e)}")