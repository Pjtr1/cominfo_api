from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from models import UserRole
import models
from datetime import datetime
from enum import Enum
#====================================================================
#user table
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.customer  # allow specifying role, default to customer


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    model_config = {
        "from_attributes": True  # allows returning ORM objects directly
    }
class UserLogin(BaseModel):
    email: str
    password: str
#=========================================================
#restaurant table
# ============================================

class RestaurantResponse(BaseModel):
    id: int
    name: str
    image_url: str | None

    canteen_id: int | None
    owner_id: int | None

    latitude: float | None
    longitude: float | None

    is_open: bool
    utilization: int | None #nullable field must specify "None" otherwise u get error when receive null

    payment_qr_url: str | None

    model_config = {
        "from_attributes": True #SQLAlchemy object > Pydantic schema > JSON
    }

#============================================================
#canteen table
#===========================================================
class CanteenResponse(BaseModel):
    id: int
    name: str
    utilization: int
    latitude: float
    longitude: float
    image_url: str | None

    model_config = {
        "from_attributes": True
    }


#======================================
#MENU TABLES
#========================================
class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    is_available: bool
    image_url: str | None

    model_config = {"from_attributes": True}


class MenuCategoryResponse(BaseModel):
    id: int
    name: str
    menu_items: list[MenuItemResponse]

    model_config = {"from_attributes": True}

#======================================
#ORDER TABLES
#========================================

class OrderCountResponse(BaseModel):
    restaurant_id: int
    active_order_count: int

class RestaurantActiveOrderCount(BaseModel):
    restaurant_id: int
    active_order_count: int


class OrderItemCreate(BaseModel):
    menu_item_id: int
    quantity: int

class OrderCreate(BaseModel):
    customer_id: int
    restaurant_id: int
    items: list[OrderItemCreate]
class OrderItemResponse(BaseModel):
    menu_item_id: int
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    restaurant_id: int
    total_price: float
    status: models.OrderStatus
    created_at: datetime
    order_items: list[OrderItemResponse]
    payment_status: PaymentStatusEnum

    model_config = {"from_attributes": True}

class CustomerOrderItemResponse(BaseModel):
    menu_item_id: int
    name: str            # include item name
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class CustomerOrderResponse(OrderResponse):
    customer_id: int
    restaurant_name: str

    # Override order_items with the new model that includes name
    order_items: List[CustomerOrderItemResponse]

    model_config = {"from_attributes": True}

class OrderStatusEnum(str, Enum):
    pending = "pending"
    preparing = "preparing"
    ready = "ready"
    completed = "completed"
    cancelled = "cancelled"


class PaymentStatusEnum(str, Enum):
    unpaid = "unpaid"
    paid = "paid"
    # Schema for returning order status
class OrderStatusResponse(BaseModel):
    order_id: int
    status: OrderStatusEnum
    payment_status: PaymentStatusEnum

    model_config = {
        "from_attributes": True
    }
class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    payment_status: Optional[PaymentStatusEnum] = None

class OrderOut(BaseModel):
    id: int
    status: OrderStatusEnum
    payment_status: PaymentStatusEnum

class Config:
        from_attributes = True  # if using SQLAlchemy

#==========================================================
#llm(planner) output
# =========================================================
class LLMCall(BaseModel):
    function: str
    args: Dict[str, Any]

class LLMPlannerResponse(BaseModel):
    calls: List[LLMCall]

#========================================================
#ai stuff idk
#========================================================
class AIMessageRequest(BaseModel):
    message: str
    latitude: float  # user's latitude
    longitude: float

class RestaurantPaymentQRResponse(BaseModel):
    restaurant_id: int
    payment_qr_url: Optional[str]

    model_config = {
        "from_attributes": True
    }
class RestaurantCreate(BaseModel):
    name: str
    owner_id: Optional[int] = None
    canteen_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_open: Optional[bool] = True
    utilization: Optional[int] = 0
    image_url: Optional[str] = None
    payment_qr_url: Optional[str] = None

# output schema for returning a restaurant
class RestaurantResponse(BaseModel):
    id: int
    name: str
    image_url: Optional[str]
    canteen_id: Optional[int]
    owner_id: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    is_open: bool
    utilization: Optional[int]
    payment_qr_url: Optional[str]

    model_config = {"from_attributes": True}

class MenuCategoryCreate(BaseModel):
    name: str

class MenuItemCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    is_available: Optional[bool] = True


class PromptPayQRRequest(BaseModel):
    promptpay_id: str  = "0829092562"
    amount: float


class PromptPayQRResponse(BaseModel):
    qr_url: str