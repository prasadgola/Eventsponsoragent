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
    
    Args:
        criteria: Search criteria (e.g., "tech companies in San Francisco")
        api_key: Apollo API key provided by user in session
    
    Returns:
        JSON list of leads
    """
    try:
        # For demo purposes, return mock data
        # In production, uncomment the real API call below:
        
        # Real API call (commented out for now):
        # headers = {
        #     "Authorization": f"Bearer {request.api_key}",
        #     "Content-Type": "application/json"
        # }
        # response = requests.post(
        #     APOLLO_API_URL,
        #     headers=headers,
        #     json={
        #         "q_keywords": request.criteria,
        #         "page": 1,
        #         "per_page": 10
        #     }
        # )
        # response.raise_for_status()
        # return response.json()
        
        # Mock response based on criteria
        print(f"🔍 Apollo search: {request.criteria}")
        
        mock_leads = [
            {
                "name": "TechCorp Solutions",
                "domain": "techcorp.com",
                "industry": "Technology",
                "size": "500-1000 employees",
                "location": "San Francisco, CA"
            },
            {
                "name": "InnovateLabs",
                "domain": "innovatelabs.io",
                "industry": "Software Development",
                "size": "100-500 employees",
                "location": "Austin, TX"
            },
            {
                "name": "CloudScale Inc",
                "domain": "cloudscale.com",
                "industry": "Cloud Services",
                "size": "1000+ employees",
                "location": "Seattle, WA"
            },
            {
                "name": "DataDriven Analytics",
                "domain": "datadriven.ai",
                "industry": "Data Analytics",
                "size": "50-100 employees",
                "location": "Boston, MA"
            },
            {
                "name": "FutureTech Ventures",
                "domain": "futuretech.vc",
                "industry": "Venture Capital",
                "size": "20-50 employees",
                "location": "Palo Alto, CA"
            }
        ]
        
        return mock_leads
        
    except Exception as e:
        print(f"❌ Apollo API error: {e}")
        raise HTTPException(status_code=500, detail=f"Apollo API error: {str(e)}")


@router.post("/clay/enrich-leads")
async def enrich_leads_with_clay(request: EnrichLeadsRequest):
    """
    Enrich lead data using Clay API
    
    Args:
        leads_json: JSON string of leads from Apollo
        api_key: Clay API key provided by user in session
    
    Returns:
        JSON list of enriched leads with contact info
    """
    try:
        # Parse the incoming JSON
        leads = json.loads(request.leads_json)
        print(f"💎 Clay enriching {len(leads)} leads")
        
        # For demo purposes, return enriched mock data
        # In production, uncomment the real API call below:
        
        # Real API call (commented out for now):
        # headers = {
        #     "Authorization": f"Bearer {request.api_key}",
        #     "Content-Type": "application/json"
        # }
        # response = requests.post(
        #     CLAY_API_URL,
        #     headers=headers,
        #     json={"companies": leads}
        # )
        # response.raise_for_status()
        # return response.json()
        
        # Mock enrichment - add email, phone, and contact info
        enriched_leads = []
        for lead in leads:
            domain = lead.get('domain', 'example.com')
            company_name = lead.get('name', 'Company')
            
            enriched_lead = {
                **lead,
                "email": f"partnerships@{domain}",
                "phone": "+1-555-" + str(hash(domain) % 10000).zfill(4),
                "decision_maker": f"VP of Partnerships",
                "decision_maker_email": f"vp@{domain}",
                "linkedin": f"https://linkedin.com/company/{company_name.lower().replace(' ', '-')}",
                "employee_count": lead.get('size', 'Unknown'),
                "revenue_range": "$10M - $50M",
                "technologies": ["Salesforce", "HubSpot", "Slack", "Google Workspace"],
                "funding_stage": "Series B" if "500+" in lead.get('size', '') else "Seed/Series A"
            }
            enriched_leads.append(enriched_lead)
        
        print(f"✅ Enriched {len(enriched_leads)} leads with Clay")
        return enriched_leads
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in leads_json")
    except Exception as e:
        print(f"❌ Clay API error: {e}")
        raise HTTPException(status_code=500, detail=f"Clay API error: {str(e)}")


@router.post("/hubspot/sync-contacts")
async def sync_contacts_to_hubspot(request: SyncContactsRequest):
    """
    Sync companies and contacts to HubSpot CRM
    
    This creates both:
    1. Company records (for the sponsor organizations)
    2. Contact records (for decision makers at those companies)
    
    Args:
        contacts_json: JSON string of enriched contacts from Clay
    
    Returns:
        Success message with sync statistics
    """
    try:
        # Get HubSpot OAuth token for demo_user from persistent storage
        access_token = get_user_token('demo_user', 'hubspot')
        
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="HubSpot not connected. Please connect HubSpot in Settings first."
            )
        
        # Parse contacts JSON
        leads = json.loads(request.contacts_json)
        print(f"📤 Syncing {len(leads)} companies to HubSpot")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Track results
        successful_companies = 0
        successful_contacts = 0
        failed_uploads = 0
        uploaded_items = []
        
        for lead in leads:
            try:
                company_name = lead.get("name", "Unknown Company")
                
                # ============================================================
                # STEP 1: Create Company in HubSpot
                # ============================================================
                company_data = {
                    "properties": {
                        "name": company_name,
                        "domain": lead.get("domain", ""),
                        "industry": lead.get("industry", ""),
                        "phone": lead.get("phone", ""),
                        "city": lead.get("location", "").split(",")[0].strip() if lead.get("location") else "",
                        "state": lead.get("location", "").split(",")[-1].strip() if "," in lead.get("location", "") else "",
                        "website": f"https://{lead.get('domain', '')}",
                        "numberofemployees": lead.get("size", ""),
                        "linkedinbio": lead.get("linkedin", ""),
                        "hs_lead_status": "NEW"
                    }
                }
                
                # PRODUCTION: Make real API call to HubSpot
                company_response = requests.post(
                    "https://api.hubapi.com/crm/v3/objects/companies",
                    headers=headers,
                    json=company_data
                )
                company_response.raise_for_status()
                company_id = company_response.json().get('id')
                
                successful_companies += 1
                print(f"  ✅ Created company: {company_name} (ID: {company_id})")
                
                # ============================================================
                # STEP 2: Create Contact (Decision Maker) in HubSpot
                # ============================================================
                decision_maker = lead.get("decision_maker", "")
                decision_maker_email = lead.get("decision_maker_email", lead.get("email", ""))
                
                if decision_maker and decision_maker_email:
                    # Parse decision maker name
                    dm_parts = decision_maker.split(" at ")[0].strip().split()
                    firstname = dm_parts[0] if dm_parts else "Decision"
                    lastname = " ".join(dm_parts[1:]) if len(dm_parts) > 1 else "Maker"
                    
                    contact_data = {
                        "properties": {
                            "firstname": firstname,
                            "lastname": lastname,
                            "email": decision_maker_email,
                            "company": company_name,
                            "jobtitle": decision_maker,
                            "phone": lead.get("phone", ""),
                            "hs_lead_status": "NEW",
                            "lifecyclestage": "lead"
                        }
                    }
                    
                    # PRODUCTION: Make real API calls to HubSpot
                    contact_response = requests.post(
                        "https://api.hubapi.com/crm/v3/objects/contacts",
                        headers=headers,
                        json=contact_data
                    )
                    contact_response.raise_for_status()
                    contact_id = contact_response.json().get('id')
                    
                    # Associate contact with company
                    association_data = {
                        "inputs": [{
                            "from": {"id": str(contact_id)},
                            "to": {"id": str(company_id)},
                            "type": "contact_to_company"
                        }]
                    }
                    assoc_response = requests.post(
                        "https://api.hubapi.com/crm/v4/associations/contacts/companies/batch/create",
                        headers=headers,
                        json=association_data
                    )
                    assoc_response.raise_for_status()
                    
                    successful_contacts += 1
                    print(f"  ✅ Created contact: {firstname} {lastname} (ID: {contact_id})")
                
                uploaded_items.append({
                    "company": company_name,
                    "contact": decision_maker if decision_maker else "N/A"
                })
                
            except Exception as e:
                print(f"  ❌ Failed: {company_name} - {e}")
                failed_uploads += 1
        
        # Create detailed success message
        message_parts = []
        if successful_companies > 0:
            message_parts.append(f"{successful_companies} companies")
        if successful_contacts > 0:
            message_parts.append(f"{successful_contacts} contacts")
        
        message = f"Successfully synced {' and '.join(message_parts)} to HubSpot CRM!"
        if failed_uploads > 0:
            message += f" ({failed_uploads} failed)"
        
        return {
            "status": "success",
            "message": message,
            "details": {
                "companies_created": successful_companies,
                "contacts_created": successful_contacts,
                "failed": failed_uploads,
                "total": len(leads),
                "uploaded_items": uploaded_items
            }
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in contacts_json")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ HubSpot sync error: {e}")
        raise HTTPException(status_code=500, detail=f"HubSpot sync error: {str(e)}")