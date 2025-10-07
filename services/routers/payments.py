from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.ap2_mock import get_credential_provider

router = APIRouter()

class CreateCartRequest(BaseModel):
    event_name: str
    tier: str
    price: str
    user_name: str
    user_email: str

class ProcessPaymentRequest(BaseModel):
    cart_id: str
    payment_method_id: str
    otp: str = ""

@router.get("/tiers")
async def get_sponsorship_tiers(event_type: str = ""):
    """Get available sponsorship tiers"""
    
    # Standard tiers for all events
    tiers = [
        {
            "name": "Gold",
            "price": "$10,000",
            "benefits": [
                "Logo prominently displayed on main stage",
                "5 exhibition booth spaces",
                "10 complimentary tickets",
                "Featured in all promotional materials",
                "Speaking opportunity at event"
            ]
        },
        {
            "name": "Silver",
            "price": "$5,000",
            "benefits": [
                "Logo on event website",
                "2 exhibition booth spaces",
                "5 complimentary tickets",
                "Mentioned in email campaigns"
            ]
        },
        {
            "name": "Bronze",
            "price": "$2,500",
            "benefits": [
                "Logo on event materials",
                "1 exhibition booth space",
                "2 complimentary tickets"
            ]
        }
    ]
    
    return {
        "tiers": tiers,
        "event_type": event_type or "all"
    }

@router.post("/create-cart")
async def create_cart(request: CreateCartRequest):
    """
    Create sponsorship cart with AP2 Intent Mandate
    """
    try:
        provider = get_credential_provider()
        
        result = provider.create_intent_mandate(
            event_name=request.event_name,
            tier=request.tier,
            price=request.price,
            user_name=request.user_name,
            user_email=request.user_email
        )
        
        return {
            "success": True,
            "cart_id": result["cart_id"],
            "intent_mandate": result["intent_mandate"],
            "cart_summary": {
                "event": request.event_name,
                "tier": request.tier,
                "amount": request.price,
                "sponsor": request.user_name
            },
            "message": f"Cart created! {request.tier} sponsorship for {request.event_name}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-methods")
async def get_payment_methods(cart_id: str):
    """
    Get available payment methods (mock cards)
    Creates AP2 Cart Mandate when payment method is shown
    """
    try:
        provider = get_credential_provider()
        
        # Get available payment methods
        payment_methods = provider.get_payment_methods()
        
        return {
            "success": True,
            "cart_id": cart_id,
            "payment_methods": payment_methods,
            "message": "Choose a payment method to continue"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process")
async def process_payment(request: ProcessPaymentRequest):
    """
    Process payment with AP2 Payment Mandate
    """
    try:
        provider = get_credential_provider()
        
        # First create cart mandate
        cart_mandate = provider.create_cart_mandate(
            cart_id=request.cart_id,
            payment_method_id=request.payment_method_id
        )
        
        # Then process payment
        result = provider.process_payment(
            cart_id=request.cart_id,
            payment_method_id=request.payment_method_id,
            otp=request.otp
        )
        
        receipt = result["receipt"]
        
        message = f"""
Payment Successful! 🎉

Receipt Details:
━━━━━━━━━━━━━━━━━━━━━━
Event: {receipt['event_name']}
Tier: {receipt['tier']}
Amount: {receipt['amount']}
Sponsor: {receipt['sponsor_name']}
Email: {receipt['sponsor_email']}
Payment: {receipt['payment_method']}
Status: {receipt['status']}
━━━━━━━━━━━━━━━━━━━━━━

Receipt ID: {receipt['receipt_id']}
Transaction ID: {receipt['transaction_id']}
Date: {receipt['date']}

Thank you for your sponsorship!
        """
        
        return {
            "success": True,
            "transaction_id": result["transaction_id"],
            "receipt": receipt,
            "message": message.strip()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transaction/{transaction_id}")
async def get_transaction(transaction_id: str):
    """Get transaction details"""
    try:
        provider = get_credential_provider()
        transaction = provider.get_transaction(transaction_id)
        
        return {
            "success": True,
            "transaction": transaction
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))