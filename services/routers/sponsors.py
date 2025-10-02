from fastapi import APIRouter
from core.airtable import get_airtable_sponsors

router = APIRouter()

@router.get("/list")
async def list_sponsors(category: str = ""):
    """Get list of sponsors from Airtable"""
    
    sponsors = get_airtable_sponsors()
    
    # Filter by category if provided
    if category:
        sponsors = [s for s in sponsors if s.get('category', '').lower() == category.lower()]
    
    return {"sponsors": sponsors, "count": len(sponsors)}

@router.get("/opportunities")
async def sponsor_opportunities(industry: str = "", budget: str = ""):
    """Find events seeking sponsorship (placeholder)"""
    
    # TODO: Implement based on your data source
    return {
        "opportunities": [
            {
                "event_id": "evt_001",
                "name": "Tech Conference 2025",
                "industry": "technology",
                "tiers": [
                    {"name": "Gold", "price": "$10,000"},
                    {"name": "Silver", "price": "$5,000"}
                ]
            }
        ]
    }