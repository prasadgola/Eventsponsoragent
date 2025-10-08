"""
Real Stripe Payment Provider with AP2 Integration
Processes real card payments via Stripe while maintaining AP2 mandate flow
"""

import os
import stripe
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Initialize Stripe
stripe_secret = os.getenv('STRIPE_SECRET_KEY')
if stripe_secret:
    stripe.api_key = stripe_secret
else:
    print("⚠️ STRIPE_SECRET_KEY not found")

class StripeCredentialProvider:
    """Real Stripe integration with AP2 mandates"""
    
    def __init__(self):
        self.carts = {}
        self.transactions = {}

        if not stripe.api_key:
            print("⚠️ Warning: STRIPE_SECRET_KEY not configured")
    
    
    def create_intent_mandate(
        self,
        event_name: str,
        tier: str,
        price: str,
        user_name: str,
        user_email: str
    ) -> Dict[str, Any]:
        """
        Create AP2 Intent Mandate + Stripe Payment Intent
        """
        cart_id = f"cart_{uuid.uuid4().hex[:12]}"
        
        # Parse price (remove $ and commas)
        price_clean = price.replace('$', '').replace(',', '')
        amount = float(price_clean)
        amount_cents = int(amount * 100)  # Stripe uses cents
        
        try:
            # Create Stripe Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                description=f"{tier} Sponsorship - {event_name}",
                metadata={
                    'cart_id': cart_id,
                    'event_name': event_name,
                    'tier': tier,
                    'sponsor_name': user_name,
                    'sponsor_email': user_email
                }
            )
            
            # Create AP2 Intent Mandate
            intent_mandate = {
                "mandate_type": "intent",
                "mandate_id": f"intent_{uuid.uuid4().hex[:12]}",
                "created_at": datetime.now().isoformat(),
                "user": {
                    "name": user_name,
                    "email": user_email
                },
                "intent": {
                    "action": "sponsor_event",
                    "event_name": event_name,
                    "tier": tier,
                    "amount": amount,
                    "currency": "USD"
                },
                "stripe_payment_intent_id": payment_intent.id,
                "status": "pending_cart"
            }
            
            # Store cart
            self.carts[cart_id] = {
                "cart_id": cart_id,
                "intent_mandate": intent_mandate,
                "stripe_payment_intent": payment_intent,
                "items": [
                    {
                        "description": f"{tier} Sponsorship for {event_name}",
                        "amount": amount,
                        "currency": "USD"
                    }
                ],
                "total": amount,
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "cart_id": cart_id,
                "intent_mandate": intent_mandate,
                "cart": self.carts[cart_id],
                "client_secret": payment_intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")
    
    def get_payment_methods(self, customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get payment methods
        For now, returns empty list - user will add card during checkout
        In production, you'd retrieve saved cards for returning customers
        """
        # For test mode, return empty list
        # User will enter card details using Stripe Elements
        return []
    
    def create_cart_mandate(
        self,
        cart_id: str,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create AP2 Cart Mandate
        In Stripe flow, this happens when user confirms payment
        """
        if cart_id not in self.carts:
            raise ValueError(f"Cart {cart_id} not found")
        
        cart = self.carts[cart_id]
        
        cart_mandate = {
            "mandate_type": "cart",
            "mandate_id": f"cart_mandate_{uuid.uuid4().hex[:12]}",
            "created_at": datetime.now().isoformat(),
            "cart_id": cart_id,
            "intent_mandate_id": cart["intent_mandate"]["mandate_id"],
            "items": cart["items"],
            "total": cart["total"],
            "currency": "USD",
            "payment_method_id": payment_method_id,
            "status": "pending_payment"
        }
        
        # Update cart
        cart["cart_mandate"] = cart_mandate
        cart["status"] = "pending_payment"
        
        return cart_mandate
    
    def confirm_payment(
        self,
        cart_id: str,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Record payment completion after Stripe confirmation"""
        if cart_id not in self.carts:
            raise ValueError(f"Cart {cart_id} not found")
        
        cart = self.carts[cart_id]

        
        # Create cart mandate if not exists
        if "cart_mandate" not in cart:
            self.create_cart_mandate(cart_id, payment_method_id)
        
        # Create AP2 Payment Mandate
        transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
        
        payment_mandate = {
            "mandate_type": "payment",
            "mandate_id": f"payment_{uuid.uuid4().hex[:12]}",
            "created_at": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "cart_id": cart_id,
            "cart_mandate_id": cart.get("cart_mandate", {}).get("mandate_id"),
            "intent_mandate_id": cart["intent_mandate"]["mandate_id"],
            "amount": cart["total"],
            "currency": "USD",
            "payment_method_id": payment_method_id,
            "stripe_payment_intent_id": cart["stripe_payment_intent"].id,
            "status": "completed"
        }
        
        # Store transaction
        self.transactions[transaction_id] = {
            "transaction_id": transaction_id,
            "payment_mandate": payment_mandate,
            "cart": cart,
            "stripe_payment_intent": cart["stripe_payment_intent"],
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }
        
        # Update cart
        cart["payment_mandate"] = payment_mandate
        cart["status"] = "completed"
        cart["transaction_id"] = transaction_id
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "payment_mandate": payment_mandate,
            "receipt": self._generate_receipt(transaction_id)
        }
    
    def _generate_receipt(self, transaction_id: str) -> Dict[str, Any]:
        """Generate a receipt for the transaction"""
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        txn = self.transactions[transaction_id]
        cart = txn["cart"]
        intent = cart["intent_mandate"]["intent"]
        
        return {
            "receipt_id": f"rcpt_{uuid.uuid4().hex[:12]}",
            "transaction_id": transaction_id,
            "date": txn["completed_at"],
            "sponsor_name": cart["intent_mandate"]["user"]["name"],
            "sponsor_email": cart["intent_mandate"]["user"]["email"],
            "event_name": intent["event_name"],
            "tier": intent["tier"],
            "amount": f"${cart['total']:,.2f}",
            "currency": "USD",
            "payment_method": f"Card ending in {txn['payment_mandate']['payment_method_id'][-4:]}",
            "stripe_charge_id": txn["payment_mandate"].get("stripe_charge_id"),
            "status": "PAID"
        }
    
    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details"""
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        return self.transactions[transaction_id]
    
    def get_client_secret(self, cart_id: str) -> str:
        """Get Stripe client secret for frontend"""
        if cart_id not in self.carts:
            raise ValueError(f"Cart {cart_id} not found")
        
        return self.carts[cart_id]["stripe_payment_intent"].client_secret

# Global instance
_stripe_provider = StripeCredentialProvider()

def get_stripe_provider() -> StripeCredentialProvider:
    """Get the global Stripe provider instance"""
    return _stripe_provider