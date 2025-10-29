from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import json
import re
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

def parse_employee_count(size_str: str) -> int:
    """
    Parse employee count string into a number for HubSpot
    Examples:
    - "500-1000 employees" -> 750
    - "100-500 employees" -> 300
    - "50-100 employees" -> 75
    - "1000+ employees" -> 1000
    """
    if not size_str:
        return None
    
    # Extract numbers
    numbers = re.findall(r'\d+', size_str)
    
    if not numbers:
        return None
    
    if len(numbers) == 1:
        # Single number like "1000+"
        return int(numbers[0])
    elif len(numbers) >= 2:
        # Range like "500-1000"
        return (int(numbers[0]) + int(numbers[1])) // 2
    
    return None


def map_industry_to_hubspot(industry_str: str) -> str:
    """
    Map our industry values to HubSpot's allowed industry values
    
    HubSpot has a strict list of allowed industries. This function maps
    common industry names to their HubSpot equivalents.
    """
    if not industry_str:
        return None
    
    industry_lower = industry_str.lower()
    
    # Mapping dictionary - maps our values to HubSpot's allowed values
    industry_map = {
        # Tech & Software
        "technology": "COMPUTER_SOFTWARE",
        "software": "COMPUTER_SOFTWARE",
        "software development": "COMPUTER_SOFTWARE",
        "saas": "COMPUTER_SOFTWARE",
        "it": "INFORMATION_TECHNOLOGY_AND_SERVICES",
        "information technology": "INFORMATION_TECHNOLOGY_AND_SERVICES",
        "cloud": "COMPUTER_SOFTWARE",
        "cloud services": "COMPUTER_SOFTWARE",
        
        # Data & Analytics
        "data": "INFORMATION_TECHNOLOGY_AND_SERVICES",
        "data analytics": "INFORMATION_TECHNOLOGY_AND_SERVICES",
        "analytics": "INFORMATION_TECHNOLOGY_AND_SERVICES",
        "data science": "INFORMATION_TECHNOLOGY_AND_SERVICES",
        
        # Finance & Investment
        "venture capital": "VENTURE_CAPITAL_PRIVATE_EQUITY",
        "private equity": "VENTURE_CAPITAL_PRIVATE_EQUITY",
        "investment": "INVESTMENT_MANAGEMENT",
        "finance": "FINANCIAL_SERVICES",
        "fintech": "FINANCIAL_SERVICES",
        
        # Consulting
        "consulting": "MANAGEMENT_CONSULTING",
        "consulting services": "MANAGEMENT_CONSULTING",
        
        # Marketing & Advertising
        "marketing": "MARKETING_AND_ADVERTISING",
        "advertising": "MARKETING_AND_ADVERTISING",
        "digital marketing": "MARKETING_AND_ADVERTISING",
        
        # E-commerce & Retail
        "ecommerce": "INTERNET",
        "e-commerce": "INTERNET",
        "retail": "RETAIL",
        
        # Healthcare
        "healthcare": "HOSPITAL_HEALTH_CARE",
        "health": "HOSPITAL_HEALTH_CARE",
        "medical": "MEDICAL_DEVICES",
        
        # Manufacturing
        "manufacturing": "AUTOMOTIVE",
        
        # Media & Entertainment
        "media": "ONLINE_MEDIA",
        "entertainment": "ENTERTAINMENT",
        
        # Default fallback
        "other": "COMPUTER_SOFTWARE"
    }
    
    # Try to find a match
    for key, value in industry_map.items():
        if key in industry_lower:
            return value
    
    # If no match found, return a safe default
    return "COMPUTER_SOFTWARE"

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
        errors = []
        
        for lead in leads:
            try:
                company_name = lead.get("name", "Unknown Company")
                
                # ============================================================
                # STEP 1: Create Company in HubSpot
                # ============================================================
                
                # Parse location
                location = lead.get("location", "")
                city = ""
                state = ""
                if location:
                    parts = [p.strip() for p in location.split(",")]
                    if len(parts) >= 1:
                        city = parts[0]
                    if len(parts) >= 2:
                        state = parts[1]
                
                # Parse employee count
                employee_count = parse_employee_count(lead.get("size", ""))
                
                # Build company properties - ONLY include non-empty values
                company_properties = {
                    "name": company_name,
                }
                
                # Add optional fields only if they have values
                if lead.get("domain"):
                    company_properties["domain"] = lead.get("domain")
                    company_properties["website"] = f"https://{lead.get('domain')}"
                
                if lead.get("industry"):
                    # Map to HubSpot's allowed industry values
                    hubspot_industry = map_industry_to_hubspot(lead.get("industry"))
                    if hubspot_industry:
                        company_properties["industry"] = hubspot_industry
                
                if lead.get("phone"):
                    company_properties["phone"] = lead.get("phone")
                
                if city:
                    company_properties["city"] = city
                
                if state:
                    company_properties["state"] = state
                
                if employee_count:
                    company_properties["numberofemployees"] = employee_count
                
                if lead.get("linkedin"):
                    company_properties["linkedin_company_page"] = lead.get("linkedin")
                
                # Always set lead status
                company_properties["hs_lead_status"] = "NEW"
                
                company_data = {
                    "properties": company_properties
                }
                
                print(f"  📤 Creating company: {company_name}")
                print(f"     Properties: {json.dumps(company_properties, indent=2)}")
                
                # PRODUCTION: Make real API call to HubSpot
                company_response = requests.post(
                    "https://api.hubapi.com/crm/v3/objects/companies",
                    headers=headers,
                    json=company_data
                )
                
                if company_response.status_code not in [200, 201]:
                    error_detail = company_response.text
                    print(f"  ❌ Company creation failed: {error_detail}")
                    errors.append(f"{company_name}: {error_detail[:200]}")
                    failed_uploads += 1
                    continue
                
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
                    
                    contact_properties = {
                        "firstname": firstname,
                        "lastname": lastname,
                        "email": decision_maker_email,
                        "company": company_name,
                        "jobtitle": decision_maker,
                        "hs_lead_status": "NEW",
                        "lifecyclestage": "lead"
                    }
                    
                    # Add phone if available
                    if lead.get("phone"):
                        contact_properties["phone"] = lead.get("phone")
                    
                    contact_data = {
                        "properties": contact_properties
                    }
                    
                    print(f"  📤 Creating contact: {firstname} {lastname}")
                    
                    # PRODUCTION: Make real API calls to HubSpot
                    contact_response = requests.post(
                        "https://api.hubapi.com/crm/v3/objects/contacts",
                        headers=headers,
                        json=contact_data
                    )
                    
                    if contact_response.status_code not in [200, 201]:
                        error_detail = contact_response.text
                        print(f"  ⚠️  Contact creation failed (company still created): {error_detail[:200]}")
                        # Don't count as failed since company was created
                    else:
                        contact_id = contact_response.json().get('id')
                        
                        # Associate contact with company
                        try:
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
                        except Exception as e:
                            print(f"  ⚠️  Contact created but association failed: {e}")
                            successful_contacts += 1
                
                uploaded_items.append({
                    "company": company_name,
                    "contact": decision_maker if decision_maker else "N/A"
                })
                
            except Exception as e:
                print(f"  ❌ Failed: {company_name} - {e}")
                errors.append(f"{company_name}: {str(e)[:200]}")
                failed_uploads += 1
        
        # Create detailed success message
        message_parts = []
        if successful_companies > 0:
            message_parts.append(f"{successful_companies} companies")
        if successful_contacts > 0:
            message_parts.append(f"{successful_contacts} contacts")
        
        if not message_parts:
            message = "Failed to sync any contacts to HubSpot. See errors below."
        else:
            message = f"Successfully synced {' and '.join(message_parts)} to HubSpot CRM!"
            if failed_uploads > 0:
                message += f" ({failed_uploads} failed)"
        
        result = {
            "status": "success" if successful_companies > 0 else "error",
            "message": message,
            "details": {
                "companies_created": successful_companies,
                "contacts_created": successful_contacts,
                "failed": failed_uploads,
                "total": len(leads),
                "uploaded_items": uploaded_items
            }
        }
        
        # Add errors if any
        if errors:
            result["errors"] = errors
        
        return result
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in contacts_json")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ HubSpot sync error: {e}")
        raise HTTPException(status_code=500, detail=f"HubSpot sync error: {str(e)}")