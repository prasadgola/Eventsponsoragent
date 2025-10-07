"""
Mock AP2 Credential Provider
Simulates payment processing with AP2 mandates without real charges
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List

class MockCredentialProvider:
    """Mock credential provider simulating Stripe/PayPal with AP2"""
    
    def __init__(self):
        # Mock payment methods (cards)
        self.payment_methods = [
            {
                "id": "pm_visa_4242",
                "type": "card",
                "brand": "Visa",
                "last4": "4242",
                "exp_month": 12,
                "exp_year": 2026,
                "name": "Test User"
            },
            {
                "id": "pm_mastercard_5555",
                "type": "card",
                "brand": "Mastercard",
                "last4": "5555",
                "exp_month": 10,
                "exp_year": 2027,
                "name": "Test User"
            },
            {
                "id": "pm_amex_3782",
                "type": "card",
                "brand": "American Express",
                "last4": "3782",
                "exp_month": 6,
                "exp_year": 2025,
                "name": "Test User"
            }
        ]
        
        # Store carts and transactions in memory
        self.carts = {}
        self.transactions = {}
    
    def create_intent_mandate(
        self,
        event_name: str,
        tier: str,
        price: str,
        user_name: str,
        user_email: str
    ) -> Dict[str, Any]:
        """
        Create AP2 Intent Mandate
        This represents user's intent to sponsor an event
        """
        cart_id = f"cart_{uuid.uuid4().hex[:12]}"
        
        # Parse price (remove $ and commas)
        price_clean = price.replace('$', '').replace(',', '')
        amount = float(price_clean)
        
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
            "status": "pending_cart"
        }
        
        # Store cart
        self.carts[cart_id] = {
            "cart_id": cart_id,
            "intent_mandate": intent_mandate,
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
            "cart": self.carts[cart_id]
        }
    
    def get_payment_methods(self) -> List[Dict[str, Any]]:
        """Get available payment methods"""
        return self.payment_methods
    
    def create_cart_mandate(self, cart_id: str, payment_method_id: str) -> Dict[str, Any]:
        """
        Create AP2 Cart Mandate
        This represents user's approval of the specific cart contents
        """
        if cart_id not in self.carts:
            raise ValueError(f"Cart {cart_id} not found")
        
        cart = self.carts[cart_id]
        
        # Find payment method
        payment_method = next(
            (pm for pm in self.payment_methods if pm["id"] == payment_method_id),
            None
        )
        if not payment_method:
            raise ValueError(f"Payment method {payment_method_id} not found")
        
        cart_mandate = {
            "mandate_type": "cart",
            "mandate_id": f"cart_mandate_{uuid.uuid4().hex[:12]}",
            "created_at": datetime.now().isoformat(),
            "cart_id": cart_id,
            "intent_mandate_id": cart["intent_mandate"]["mandate_id"],
            "items": cart["items"],
            "total": cart["total"],
            "currency": "USD",
            "payment_method": {
                "id": payment_method_id,
                "type": payment_method["type"],
                "last4": payment_method["last4"]
            },
            "status": "pending_payment",
            "requires_otp": True
        }
        
        # Update cart
        cart["cart_mandate"] = cart_mandate
        cart["status"] = "pending_payment"
        
        return cart_mandate
    
    def process_payment(
        self,
        cart_id: str,
        payment_method_id: str,
        otp: str
    ) -> Dict[str, Any]:
        """
        Create AP2 Payment Mandate and process payment
        This is the final step that executes the transaction
        """
        if cart_id not in self.carts:
            raise ValueError(f"Cart {cart_id} not found")
        
        cart = self.carts[cart_id]
        
        # Verify OTP (mock - accept "123" or "000000")
        if otp not in ["123", "000000"]:
            raise ValueError("Invalid OTP. Please use '123' for demo.")
        
        # Create payment mandate
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
            "status": "completed",
            "otp_verified": True
        }
        
        # Store transaction
        self.transactions[transaction_id] = {
            "transaction_id": transaction_id,
            "payment_mandate": payment_mandate,
            "cart": cart,
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
            "status": "PAID"
        }
    
    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details"""
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        return self.transactions[transaction_id]

# Global instance
_credential_provider = MockCredentialProvider()

def get_credential_provider() -> MockCredentialProvider:
    """Get the global credential provider instance"""
    return _credential_provider