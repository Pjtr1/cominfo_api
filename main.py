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
from crud import get_order_status
from schemas import OrderStatusResponse

from fastapi import UploadFile, File, Form
import cloudinary.uploader

#for returning csv file(to import table data to google sheet)(not using anymore)
from fastapi.responses import Response
import csv
import io

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



# @app.post("/register", response_model=schemas.UserResponse)
# def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     existing_user = crud.get_user_by_email(db, user.email)
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#
#     return crud.create_user(db, user.username, user.email, user.password)


@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Pass the role from the schema
    return crud.create_user(db, user.username, user.email, user.password, role=user.role)

#user after def register is a variable with class of usercreate. the variable is created in that line, user.email is just the email str object in the UserCreate class(see schemas.py)


# @app.post("/login", response_model=schemas.UserResponse)
# def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
#     db_user = crud.authenticate_user(db, user.email, user.password)
#     if not db_user:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid email or password"
#         )
#
#     return db_user

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

# @app.get("/canteens/{canteen_id}/restaurants", response_model=list[schemas.RestaurantResponse])
# def get_restaurants(canteen_id: int, db: Session = Depends(get_db)):
#     restaurants = crud.get_restaurants_by_canteen(db, canteen_id)
#
#     if not restaurants:
#         return []
#
#     return restaurants

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
            order_items=[
                schemas.CustomerOrderItemResponse(
                    menu_item_id=i.menu_item_id,
                    name=i.menu_item.name,  # <-- add name here
                    quantity=i.quantity,
                    price=float(i.price)
                )
                for i in o.order_items
            ]
        )
        for o in orders
    ]


@app.get("/orders/{order_id}/status", response_model=OrderStatusResponse)
def read_order_status(order_id: int, db: Session = Depends(get_db)):
    """
    Get order status by order ID.
    """
    order = get_order_status(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderStatusResponse(order_id=order.id, status=order.status.value)

from crud import get_restaurant_payment_qr
from schemas import RestaurantPaymentQRResponse
@app.get("/restaurants/{restaurant_id}/payment_qr", response_model=RestaurantPaymentQRResponse)
def read_restaurant_payment_qr(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = get_restaurant_payment_qr(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return RestaurantPaymentQRResponse(
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
    image: UploadFile = File(None),  # <-- new: upload file
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

#start the server(for testing, will use gunicorn+uvicorn for the actual app)
#remove later
# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

