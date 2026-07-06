import os
import stripe

def create_checkout_session(order_id: str, amount: float, user_email: str, success_url: str, cancel_url: str):
    """
    Creates a Stripe Checkout Session for an order.
    Returns the session URL.
    """
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        return None
        
    stripe.api_key = stripe_key
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=user_email,
            line_items=[{
                'price_data': {
                    'currency': 'inr', # Or usd, depending on account setup
                    'product_data': {
                        'name': f'OneBasket Order #{order_id}',
                    },
                    'unit_amount': int(amount * 100), # Amount in paise/cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=order_id
        )
        return {"url": session.url, "session_id": session.id}
    except Exception as e:
        print(f"Stripe Error: {e}")
        return None

def verify_session(session_id: str):
    """
    Verifies if a Stripe checkout session was successfully paid.
    """
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        return False
        
    stripe.api_key = stripe_key
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session.payment_status == 'paid'
    except Exception as e:
        print(f"Stripe Verify Error: {e}")
        return False
