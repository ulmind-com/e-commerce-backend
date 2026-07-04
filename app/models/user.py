from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class SavedAddress(BaseModel):
    id: str
    label: str  # e.g., 'Home', 'Work', 'Other'
    flat: str = ""
    area: str = ""
    landmark: str = ""
    address: str  # Display string
    lat: float
    lng: float
    buildingName: Optional[str] = None
    buildingType: Optional[str] = None
    receiverName: Optional[str] = None
    receiverNumber: Optional[str] = None

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str = "customer"
    phone: Optional[str] = None
    google_uid: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    saved_addresses: List[SavedAddress] = []
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}

class UserResponse(UserBase):
    id: str = Field(alias="_id")
    saved_addresses: List[SavedAddress] = []
    avatar_url: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    model_config = {"populate_by_name": True, "from_attributes": True}

