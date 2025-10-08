from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.stripe_provider import get_stripe_provider

router = APIRouter()

class CreateCartRequest(BaseModel):
    event_name: str
    tier: str
    price: str
    user_name: str
    user_email: str

class ConfirmPaymentRequest(BaseModel):
    cart_id: str
    payment_method_id: str

@router.get("/tiers")
async def get_sponsorship_tiers(event_type: str = ""):
    """Get available sponsorship tiers"""
    
    tiers = [
        {
            "name": "Gold",
            "price": "$10,000",
            "emoji": "💎",
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
            "emoji": "🥈",
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
            "emoji": "🥉",
            "benefits": [
                "Logo on event materials",
                "1 exhibition booth space",
                "2 complimentary tickets"
            ]
        },
        {
            "name": "Custom",
            "price": "Any Amount ($0.50+)",
            "emoji": "✨",
            "benefits": [
                "Choose your own sponsorship amount",
                "Perfect for individuals and small businesses",
                "Every contribution helps make events possible!",
                "You'll be listed as a valued supporter",
                "From $0.50 to unlimited - all welcome!"
            ],
            "suggested_amounts": [
                "$1 - Buy a coffee for organizers ☕",
                "$5 - Cover wifi costs 📡",
                "$25 - Feed a volunteer 🍕",
                "$100 - Support event materials 📋",
                "$500 - Sponsor a speaker 🎤",
                "$1,000+ - Major impact! 🚀"
            ]
        }
    ]
    
    return {
        "tiers": tiers,
        "event_type": event_type or "all",
        "message": "Every sponsorship level is valued and appreciated! From $0.50 to unlimited, you're supporting something great."
    }

@router.post("/create-cart")
async def create_cart(request: CreateCartRequest):
    """
    Create sponsorship cart with AP2 Intent Mandate + Stripe Payment Intent
    """
    try:
        provider = get_stripe_provider()
        
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
            "client_secret": result["client_secret"],
            "intent_mandate": result["intent_mandate"],
            "cart_summary": {
                "event": request.event_name,
                "tier": request.tier,
                "amount": request.price,
                "sponsor": request.user_name
            },
            "payment_form_trigger": True,  # Trigger frontend form
            "message": f"Cart created! {request.tier} sponsorship for {request.event_name}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payment-methods")
async def get_payment_methods(cart_id: str):
    """
    Get Stripe client secret for payment
    """
    try:
        provider = get_stripe_provider()
        client_secret = provider.get_client_secret(cart_id)
        
        return {
            "success": True,
            "cart_id": cart_id,
            "client_secret": client_secret,
            "message": "Enter your card details to complete payment"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm")
async def confirm_payment(request: ConfirmPaymentRequest):
    """
    Record payment completion and create AP2 Payment Mandate
    NOTE: Stripe payment already succeeded by this point
    """
    try:
        provider = get_stripe_provider()
        
        # Get the cart
        if request.cart_id not in provider.carts:
            raise HTTPException(status_code=404, detail=f"Cart {request.cart_id} not found")
        
        cart = provider.carts[request.cart_id]
        
        # Create cart mandate if not exists
        if "cart_mandate" not in cart:
            provider.create_cart_mandate(request.cart_id, request.payment_method_id)
        
        # Create payment mandate and transaction record
        transaction_id = f"txn_{cart['cart_id'][-8:]}"
        
        payment_mandate = {
            "mandate_type": "payment",
            "mandate_id": f"payment_{transaction_id}",
            "created_at": cart.get('created_at'),
            "transaction_id": transaction_id,
            "cart_id": request.cart_id,
            "cart_mandate_id": cart.get("cart_mandate", {}).get("mandate_id"),
            "intent_mandate_id": cart["intent_mandate"]["mandate_id"],
            "amount": cart["total"],
            "currency": "USD",
            "payment_method_id": request.payment_method_id,
            "stripe_payment_intent_id": cart["stripe_payment_intent"].id,
            "status": "completed"
        }
        
        # Store transaction
        provider.transactions[transaction_id] = {
            "transaction_id": transaction_id,
            "payment_mandate": payment_mandate,
            "cart": cart,
            "stripe_payment_intent": cart["stripe_payment_intent"],
            "status": "completed",
            "completed_at": cart.get('created_at')
        }
        
        # Update cart
        cart["payment_mandate"] = payment_mandate
        cart["status"] = "completed"
        cart["transaction_id"] = transaction_id
        
        # Generate receipt
        receipt = provider._generate_receipt(transaction_id)
        
        message = f"""Payment Successful! 🎉

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
            "transaction_id": transaction_id,
            "receipt": receipt,
            "message": message.strip()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transaction/{transaction_id}")
async def get_transaction(transaction_id: str):
    """Get transaction details"""
    try:
        provider = get_stripe_provider()
        transaction = provider.get_transaction(transaction_id)
        
        return {
            "success": True,
            "transaction": transaction
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/latest-cart")
async def get_latest_cart():
    """
    Get the most recently created cart
    Used by frontend to show payment form
    """
    try:
        provider = get_stripe_provider()
        
        # Get the most recent cart (last one in dict)
        if not provider.carts:
            raise HTTPException(status_code=404, detail="No carts found")
        
        # Get last cart
        cart_id = list(provider.carts.keys())[-1]
        cart = provider.carts[cart_id]
        
        # Get client secret
        client_secret = cart["stripe_payment_intent"].client_secret
        
        # Get cart summary
        intent = cart["intent_mandate"]["intent"]
        cart_summary = {
            "event": intent["event_name"],
            "tier": intent["tier"],
            "amount": f"${intent['amount']:,.2f}"
        }
        
        return {
            "success": True,
            "cart_id": cart_id,
            "client_secret": client_secret,
            "cart_summary": cart_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))