import os
import stripe

def create_payment_intent(amount: float, currency: str = 'inr'):
    """
    Creates a Stripe PaymentIntent for inline card payment.
    Returns client_secret and payment_intent_id.
    """
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        return None
    stripe.api_key = stripe_key
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency,
            automatic_payment_methods={
                'enabled': True,
                'allow_redirects': 'never'
            },
        )
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        }
    except Exception as e:
        print(f"Stripe PaymentIntent Error: {e}")
        return None

def verify_payment_intent(payment_intent_id: str):
    """
    Verifies if a Stripe PaymentIntent was successfully paid.
    """
    stripe_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_key:
        return False
    stripe.api_key = stripe_key
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return intent.status == 'succeeded'
    except Exception as e:
        print(f"Stripe Verify Error: {e}")
        return False
