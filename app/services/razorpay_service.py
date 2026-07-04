from app.core.config import settings

client = None

def _get_client():
    global client
    if client is None:
        try:
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        except Exception as e:
            print(f"Warning: Could not initialize Razorpay client: {e}")
    return client

def create_order(amount: float, currency: str = "INR"):
    rz_client = _get_client()
    if not rz_client:
        print("Razorpay client not available")
        return None
    data = {
        "amount": int(amount * 100), # Amount in paisa
        "currency": currency,
        "payment_capture": 1
    }
    try:
        order = rz_client.order.create(data=data)
        return order
    except Exception as e:
        print(f"Error creating Razorpay order: {str(e)}")
        return None

def verify_payment_signature(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str):
    rz_client = _get_client()
    if not rz_client:
        return False
    try:
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        return rz_client.utility.verify_payment_signature(params_dict)
    except Exception as e:
        print(f"Signature verification failed: {str(e)}")
        return False
