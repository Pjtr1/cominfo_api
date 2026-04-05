from sqlalchemy.orm import Session, aliased
from models import User, UserRole, Canteen, Restaurant, MenuCategory, MenuItem, Order, OrderItem, OrderStatus
from passlib.context import CryptContext
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from typing import Optional


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#====================================================================================
#users table
def get_password_hash(password: str):
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)



def create_user(db: Session, username: str, email: str, password: str, role: UserRole = UserRole.customer):
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()






def authenticate_user(db: Session, email_or_username: str, password: str):
    # Try to find a user where email OR username matches the input
    user = db.query(User).filter(
        or_(
            User.email == email_or_username,
            User.username == email_or_username
        )
    ).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


#=========================================================================
#canteen and restaurant tables

def get_all_canteens(db: Session):
    return db.query(Canteen).all()




def get_restaurants_by_canteen(db: Session, canteen_id: Optional[int] = None):
    query = db.query(Restaurant)

    if canteen_id is None:
        return query.filter(Restaurant.canteen_id == None).all()

    return query.filter(Restaurant.canteen_id == canteen_id).all()


#======================================
#MENU TABLES
#========================================

def get_menu_by_restaurant(db: Session, restaurant_id: int):
    return (
        db.query(MenuCategory)
        .filter(MenuCategory.restaurant_id == restaurant_id)
        .all()
    )


#======================================
#ORDER TABLES
#========================================

def get_active_order_count_by_restaurant(db: Session, restaurant_id: int):
    return (
        db.query(Order)
        .filter(
            Order.restaurant_id == restaurant_id,
            Order.status.in_([OrderStatus.pending, OrderStatus.preparing])
        )
        .count()
    )


def get_active_order_counts_all_restaurants(db: Session):
    results = (
        db.query(
            Restaurant.id.label("restaurant_id"),
            func.count(Order.id).label("active_order_count")
        )
        .outerjoin(
            Order,
            (Order.restaurant_id == Restaurant.id) &
            (Order.status.in_([OrderStatus.pending, OrderStatus.preparing]))
        )
        .group_by(Restaurant.id)
        .all()
    )

    return results  # <-- you must return the query results

def create_order(db: Session, customer_id: int, order_data):
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Order is empty")

    menu_items = db.query(MenuItem).filter(
        MenuItem.id.in_([item.menu_item_id for item in order_data.items])
    ).all()

    menu_item_map = {item.id: item for item in menu_items}

    total_price = 0

    for item in order_data.items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Invalid quantity")

        menu_item = menu_item_map.get(item.menu_item_id)

        if not menu_item:
            raise HTTPException(status_code=404, detail="Item not found")

        if not menu_item.is_available:
            raise HTTPException(status_code=400, detail="Item not available")

        total_price += float(menu_item.price) * item.quantity

    order = Order(
        customer_id=customer_id,
        restaurant_id=order_data.restaurant_id,
        total_price=total_price,
        status=OrderStatus.pending
    )
    db.add(order)
    db.flush()

    for item in order_data.items:
        menu_item = menu_item_map[item.menu_item_id]

        db.add(OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=item.quantity,
            price=menu_item.price
        ))

    db.commit()
    db.refresh(order)

    return order

def get_orders_by_customer(db: Session, customer_id: int):
    orders = (
        db.query(Order)
        .filter(Order.customer_id == customer_id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return orders

def get_order_status(db: Session, order_id: int):
    """
    Get order status by order ID.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        return order
    return None




def get_restaurant_payment_qr(db: Session, restaurant_id: int):
    return db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

import models, schemas
def create_restaurant(db: Session, restaurant_data: dict):
    db_restaurant = models.Restaurant(
        name=restaurant_data["name"],
        owner_id=restaurant_data.get("owner_id"),
        canteen_id=restaurant_data.get("canteen_id"),
        latitude=restaurant_data.get("latitude"),
        longitude=restaurant_data.get("longitude"),
        is_open=restaurant_data.get("is_open", True),
        utilization=restaurant_data.get("utilization"),
        image_url=restaurant_data.get("image_url"),
        payment_qr_url=restaurant_data.get("payment_qr_url")
    )
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant