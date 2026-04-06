from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import crud
import schemas
from fastapi.middleware.cors import CORSMiddleware

from routes.ai import router as ai_router
from database import get_db

from typing import Optional

from fastapi import UploadFile, File, Form
import cloudinary.uploader

import cloudinary

import qrcode
import tempfile
from fastapi import Body


cloudinary.config(
    cloud_name = "dzft0ec99",
    api_key = "562835278438914",
    api_secret = "9LTeVUXI6J4KV5-_psoP4mqQQZc"
)
#for returning csv file(to import table data to google sheet)(not using anymore)


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)



@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Pass the role from the schema
    return crud.create_user(db, user.username, user.email, user.password, role=user.role)



@app.post("/login", response_model=schemas.UserResponse)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, email_or_username=user.email, password=user.password)
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    return db_user

@app.get("/canteens", response_model=list[schemas.CanteenResponse])
def get_canteens(db: Session = Depends(get_db)):
    return crud.get_all_canteens(db)


@app.get("/restaurants", response_model=list[schemas.RestaurantResponse])
def get_restaurants(
    canteen_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return crud.get_restaurants_by_canteen(db, canteen_id)

@app.get("/restaurants/{restaurant_id}/menu",response_model=list[schemas.MenuCategoryResponse])
def get_menu(
        restaurant_id: int,
        db: Session = Depends(get_db)
):
    return crud.get_menu_by_restaurant(db, restaurant_id)



@app.get(
    "/restaurants/{restaurant_id}/orders/active-count",
    response_model=schemas.OrderCountResponse
    )
def get_active_order_count(restaurant_id: int, db: Session = Depends(get_db)):
    count = crud.get_active_order_count_by_restaurant(db, restaurant_id)

    return {
        "restaurant_id": restaurant_id,
        "active_order_count": count
    }

@app.get(
    "/restaurants/orders/active-count",
    response_model=list[schemas.RestaurantActiveOrderCount]
)
def get_all_active_order_counts(db: Session = Depends(get_db)):
    results = crud.get_active_order_counts_all_restaurants(db)

    return [
        {
            "restaurant_id": r.restaurant_id,
            "active_order_count": r.active_order_count
        }
        for r in results
    ]

@app.post("/orders", response_model=schemas.OrderResponse)
def create_order_endpoint(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db)
):
    return crud.create_order(db, order.customer_id, order)

@app.get("/users/{customer_id}/orders", response_model=list[schemas.CustomerOrderResponse])
def get_orders_for_user(customer_id: int, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_customer(db, customer_id)
    return [
        schemas.CustomerOrderResponse(
            id=o.id,
            customer_id=o.customer_id,
            restaurant_id=o.restaurant_id,
            restaurant_name=o.restaurant.name,
            total_price=float(o.total_price),
            status=o.status,
            created_at=o.created_at,
            payment_status=o.payment_status,
            order_items=[
                schemas.CustomerOrderItemResponse(
                    menu_item_id=i.menu_item_id,
                    name=i.menu_item.name,
                    quantity=i.quantity,
                    price=float(i.price)
                )
                for i in o.order_items
            ]
        )
        for o in orders
    ]
@app.get("/restaurants/{restaurant_id}/orders", response_model=list[schemas.CustomerOrderResponse])
def get_orders_for_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_restaurant(db, restaurant_id)

    return [
        schemas.CustomerOrderResponse(
            id=o.id,
            customer_id=o.customer_id,
            restaurant_id=o.restaurant_id,
            restaurant_name=o.restaurant.name,
            total_price=float(o.total_price),
            status=o.status,
            created_at=o.created_at,
            payment_status=o.payment_status,
            order_items=[
                schemas.CustomerOrderItemResponse(
                    menu_item_id=i.menu_item_id,
                    name=i.menu_item.name,
                    quantity=i.quantity,
                    price=float(i.price)
                )
                for i in o.order_items
            ]
        )
        for o in orders
    ]

@app.get("/orders/{order_id}/status", response_model=schemas.OrderStatusResponse)
def read_order_status(order_id: int, db: Session = Depends(get_db)):
    """
    Get order status by order ID.
    """
    order = crud.get_order_status(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return schemas.OrderStatusResponse(
        order_id=order.id,
        status=order.status,
        payment_status=order.payment_status
    )

@app.patch("/orders/{order_id}", response_model=schemas.OrderOut)
def update_order_status(
    order_id: int,
    data: schemas.OrderUpdate,
    db: Session = Depends(get_db)
):
    order = crud.update_order(db, order_id, data)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


@app.get("/restaurants/{restaurant_id}/payment_qr", response_model=schemas.RestaurantPaymentQRResponse)
def read_restaurant_payment_qr(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = crud.get_restaurant_payment_qr(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return schemas.RestaurantPaymentQRResponse(
        restaurant_id=restaurant.id,
        payment_qr_url=restaurant.payment_qr_url
    )

@app.post("/restaurants", response_model=schemas.RestaurantResponse)
async def create_restaurant_endpoint(
    name: str = Form(...),
    owner_id: int = Form(None),
    canteen_id: int = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    is_open: bool = Form(True),
    utilization: int = Form(0),
    payment_qr_url: str = Form(None),
    image: UploadFile = File(None),  # upload file
    db: Session = Depends(get_db)
):
    # Prevent duplicate names
    existing = db.query(models.Restaurant).filter(models.Restaurant.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Restaurant with this name already exists")

    image_url = None
    if image:
        # Upload image to Cloudinary
        result = cloudinary.uploader.upload(
            image.file,
            folder="restaurants"
        )
        image_url = result.get("secure_url")

    # Call CRUD with image_url
    new_restaurant = crud.create_restaurant(db, {
        "name": name,
        "owner_id": owner_id,
        "canteen_id": canteen_id,
        "latitude": latitude,
        "longitude": longitude,
        "is_open": is_open,
        "utilization": utilization,
        "payment_qr_url": payment_qr_url,
        "image_url": image_url
    })
    return new_restaurant

@app.get("/users/{owner_id}/restaurants", response_model=list[schemas.RestaurantResponse])
def get_restaurants_by_owner_endpoint(owner_id: int, db: Session = Depends(get_db)):
    restaurants = crud.get_restaurants_by_owner(db, owner_id)
    return restaurants


@app.post("/restaurants/{restaurant_id}/categories", response_model=schemas.MenuCategoryResponse)
def add_menu_category(
        restaurant_id: int,
        category: schemas.MenuCategoryCreate,
        db: Session = Depends(get_db)
):
    restaurant = crud.get_restaurant_payment_qr(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return crud.create_menu_category(db, restaurant_id, category)


@app.post("/categories/{category_id}/items", response_model=schemas.MenuItemResponse)
def add_menu_item(
    category_id: int,
    name: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    is_available: Optional[bool] = Form(True),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    category = db.query(models.MenuCategory).filter(models.MenuCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    image_url = None
    if image:
        result = cloudinary.uploader.upload(image.file, folder="menu_items")
        image_url = result.get("secure_url")

    # create a MenuItemCreate instance to use with crud function
    item_data = schemas.MenuItemCreate(
        name=name,
        price=price,
        description=description,
        is_available=is_available
    )

    return crud.create_menu_item(db, category_id, item_data, image_url)

def generate_promptpay_payload(account: str, amount: float) -> str:
    """
    Generate PromptPay QR payload (EMVCo format)
    Supports phone number or national ID
    """

    def format_id(acc: str):
        acc = acc.replace("-", "").replace(" ", "").strip()

        # Remove + if exists
        if acc.startswith("+66"):
            acc = acc[3:]
            acc = "0" + acc

        # Phone number
        if acc.startswith("0") and len(acc) == 10:
            return "0066" + acc[1:]

        return acc

    def tlv(tag, value):
        return f"{tag}{len(value):02d}{value}"

    account = format_id(account)

    payload = ""
    payload += tlv("00", "01")  # Payload format
    payload += tlv("01", "11")  # Static QR

    # Merchant account info
    merchant_info = ""
    merchant_info += tlv("00", "A000000677010111")  # PromptPay AID
    merchant_info += tlv("01", account)

    payload += tlv("29", merchant_info)

    payload += tlv("52", "0000")  # MCC
    payload += tlv("53", "764")   # THB


    if amount > 0:
        payload += tlv("54", f"{amount:.2f}")

    payload += tlv("58", "TH")    # Country
    payload += tlv("59", "PromptPay")
    payload += tlv("60", "Bangkok")

    # CRC placeholder
    payload += "6304"

    # Calculate CRC
    crc = crc16(payload)
    payload += crc

    return payload


def crc16(data: str):
    crc = 0xFFFF
    for c in data:
        crc ^= ord(c) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f"{crc:04X}"

@app.post("/promptpay/qr", response_model=schemas.PromptPayQRResponse)
def create_promptpay_qr(
    data: schemas.PromptPayQRRequest,
):
    try:
        # 1. Generate payload
        payload = generate_promptpay_payload(
            data.promptpay_id,
            data.amount
        )

        # 2. Generate QR image
        qr = qrcode.make(payload)

        # 3. Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            qr.save(tmp.name)

            # 4. Upload to Cloudinary
            result = cloudinary.uploader.upload(
                tmp.name,
                folder="promptpay_qr"
            )

        return {
            "qr_url": result.get("secure_url")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#start a web server(for local tests)
#remove later for actual deployment
# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

