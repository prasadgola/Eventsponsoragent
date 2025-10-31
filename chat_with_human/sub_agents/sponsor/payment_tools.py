import requests
import json
import os
from typing import Dict, Any

SERVICES_URL = os.getenv('SERVICES_URL', 'http://localhost:8001')

def _call_service(method: str, endpoint: str, **kwargs):
    """Helper to call Services Server"""
    url = f"{SERVICES_URL}{endpoint}"
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response.json()

def create_sponsorship_cart(
    event_name: str,
    tier: str,
    price: str,
    user_name: str,
    user_email: str
) -> str:
    """
    Create a sponsorship cart with AP2 Intent Mandate.
    
    Args:
        event_name: Name of the event to sponsor
        tier: Sponsorship tier (e.g., "Gold", "Silver", "Bronze", "Custom")
        price: Price (e.g., "$10,000" or "$1" or "$0.50")
        user_name: Sponsor's name
        user_email: Sponsor's email
    
    Returns:
        JSON string with cart details including client_secret for payment form
    """
    try:
        # Parse and validate amount
        price_clean = price.replace('$', '').replace(',', '').strip()
        
        try:
            amount = float(price_clean)
        except ValueError:
            return json.dumps({
                "success": False, 
                "error": f"Invalid amount format: {price}. Please use format like $1 or $10.00"
            })
        
        # Stripe minimum is $0.50
        if amount < 0.50:
            return json.dumps({
                "success": False,
                "error": "Stripe requires a minimum payment of $0.50. Would you like to sponsor $0.50 instead?"
            })
        
        # Set reasonable maximum (optional)
        if amount > 1000000:
            return json.dumps({
                "success": False,
                "error": "For sponsorships over $1,000,000, please contact us directly for a custom package!"
            })
        
        # Call backend to create cart
        result = _call_service('POST', '/payments/create-cart', json={
            'event_name': event_name,
            'tier': tier,
            'price': f"${amount:.2f}",  # Format consistently
            'user_name': user_name,
            'user_email': user_email
        })
        
        # Return everything the frontend needs
        if result.get('success'):
            # Add encouraging message based on amount
            if amount < 10:
                encouragement = "Every dollar counts! Thank you for supporting this event! 💙"
            elif amount < 100:
                encouragement = "Your generous contribution is much appreciated! 🌟"
            elif amount < 1000:
                encouragement = "Wow! Your support means so much to us! 🎉"
            else:
                encouragement = "Incredible! Your sponsorship makes a huge impact! 🚀"
            
            return json.dumps({
                "success": True,
                "cart_id": result.get("cart_id"),
                "client_secret": result.get("client_secret"),
                "cart_summary": result.get("cart_summary"),
                "payment_form_trigger": True,
                "message": f"Cart created! {encouragement}"
            })
        else:
            return json.dumps({"success": False, "error": "Failed to create cart"})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

def get_sponsorship_tiers(event_type: str = "") -> str:
    """
    Get available sponsorship tiers with pricing.
    
    Args:
        event_type: Type of event (optional filter)
    
    Returns:
        JSON string with tier options
    """
    try:
        params = {'event_type': event_type} if event_type else {}
        result = _call_service('GET', '/payments/tiers', params=params)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

