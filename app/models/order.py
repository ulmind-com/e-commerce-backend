from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OrderItem(BaseModel):
    product_id: str
    title: Optional[str] = None  # stored for display convenience
    image_url: Optional[str] = None  # stored for display convenience
    quantity: int
    price_at_purchase: float


class DeliveryLocation(BaseModel):
    label: str = "Home"
    flat: str = ""
    area: str = ""
    landmark: str = ""
    address: str = ""
    lat: float = 0.0
    lng: float = 0.0
    buildingName: Optional[str] = None
    buildingType: Optional[str] = None
    receiverName: Optional[str] = None
    receiverNumber: Optional[str] = None

class OrderBase(BaseModel):
    user_id: str
    delivery_partner_id: Optional[str] = None
    items: List[OrderItem]
    total_amount: float
    delivery_address: Optional[str] = None  # Legacy, keeping for backwards compatibility
    delivery_location: Optional[DeliveryLocation] = None
    payment_mode: str = "COD"  # 'COD', 'ONLINE'
    payment_status: str = "Pending"  # 'Pending', 'Completed', 'Failed'
    order_status: str = "Order Placed"  # 'Order Placed', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled'
    razorpay_order_id: Optional[str] = None


class OrderCreate(BaseModel):
    """What the frontend sends — user_id is inferred from the auth token."""
    items: List[OrderItem]
    total_amount: float
    delivery_address: Optional[str] = None
    delivery_location: Optional[DeliveryLocation] = None
    payment_mode: str = "COD"


class OrderInDB(OrderBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}


class OrderResponse(OrderBase):
    id: str = Field(alias="_id")
    created_at: datetime = datetime.utcnow()

    model_config = {"populate_by_name": True, "from_attributes": True}
