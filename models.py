from sqlalchemy import Column, Integer, String, Float, ForeignKey,Text, DECIMAL,Boolean
from database import Base
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import Enum, DateTime
from sqlalchemy.sql import func
import enum  # for UserRole
#define all tables as class in python using sqlAlchemy, basically the core idea of ORM(object relational mapping)
class UserRole(enum.Enum):
    customer = "customer"
    seller = "seller"
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    #relationships
    restaurants = relationship("Restaurant", back_populates="owner")
    orders = relationship("Order", back_populates="customer", cascade="all, delete")

#"User" class will be primarily used in crud.py for db queries command

#canteen tables
class Canteen(Base):
    __tablename__ = "canteens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    utilization = Column(Integer, nullable=False, default=0)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint("utilization >= 0 AND utilization <= 100", name="canteens_utilization_0_100"),
    )
    restaurants = relationship(
        "Restaurant",
        back_populates="canteen",
        cascade="all, delete"
    )

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    image_url = Column(String(255), nullable=True)

    canteen_id = Column(Integer, ForeignKey("canteens.id"), nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # link to User
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_open = Column(Boolean, nullable=False, default=True)
    utilization = Column(Integer, nullable=True)
    payment_qr_url = Column(String(255), nullable=True)
    __table_args__ = (
        CheckConstraint("utilization >= 0 AND utilization <= 100", name="restaurants_utilization_0_100"),
    )

    # ORM relationships
    owner = relationship("User", back_populates="restaurants")  # optional: access restaurant.owner

    canteen = relationship("Canteen", back_populates="restaurants")
    menu_categories = relationship("MenuCategory", back_populates="restaurant", cascade="all, delete")
    orders = relationship("Order", back_populates="restaurant", cascade="all, delete")



# Menu category table
class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(100), nullable=False)

    # ORM relationship
    restaurant = relationship("Restaurant", back_populates="menu_categories")
    menu_items = relationship("MenuItem", back_populates="category", cascade="all, delete")


# Menu items table
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("menu_categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    image_url = Column(String(255), nullable=True)

    # ORM relationship
    category = relationship("MenuCategory", back_populates="menu_items")


# Order status enum
class OrderStatus(enum.Enum):
    pending = "pending"
    preparing = "preparing"
    ready = "ready"
    completed = "completed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    total_price = Column(DECIMAL(10,2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    customer = relationship("User", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)  # price at the time of order

    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem")