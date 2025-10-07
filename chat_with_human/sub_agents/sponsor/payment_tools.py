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
        tier: Sponsorship tier (e.g., "Gold", "Silver", "Bronze")
        price: Price (e.g., "$10,000")
        user_name: Sponsor's name
        user_email: Sponsor's email
    
    Returns:
        JSON string with cart details and mandate info
    """
    try:
        result = _call_service('POST', '/payments/create-cart', json={
            'event_name': event_name,
            'tier': tier,
            'price': price,
            'user_name': user_name,
            'user_email': user_email
        })
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

def select_payment_method(cart_id: str) -> str:
    """
    Show available payment methods (mock cards).
    
    Args:
        cart_id: Cart ID from create_sponsorship_cart
    
    Returns:
        JSON string with available payment methods
    """
    try:
        result = _call_service('GET', f'/payments/payment-methods?cart_id={cart_id}')
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

def process_payment(
    cart_id: str,
    payment_method_id: str,
    otp: str = ""
) -> str:
    """
    Process payment with AP2 Payment Mandate.
    
    Args:
        cart_id: Cart ID
        payment_method_id: Selected payment method ID
        otp: One-time password (use "123" for mock)
    
    Returns:
        Payment confirmation message
    """
    try:
        result = _call_service('POST', '/payments/process', json={
            'cart_id': cart_id,
            'payment_method_id': payment_method_id,
            'otp': otp
        })
        
        if result.get('success'):
            return f"✅ Payment successful!\n\n{result.get('message', '')}\n\nTransaction ID: {result.get('transaction_id', 'N/A')}"
        else:
            return f"❌ Payment failed: {result.get('message', 'Unknown error')}"
    except Exception as e:
        return f"❌ Payment error: {str(e)}"

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