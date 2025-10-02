from fastapi import APIRouter
from core.airtable import get_airtable_sponsors

router = APIRouter()

@router.get("/sponsors")
async def get_sponsors():
    """Get all sponsors from Airtable"""
    
    sponsors = get_airtable_sponsors()
    return {"sponsors": sponsors, "count": len(sponsors)}