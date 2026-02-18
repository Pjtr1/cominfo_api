from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship

#define all tables as class in python using sqlAlchemy, which is basically the core idea of ORM(object relational mapping)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)

#"User" class will be primarily used in crud.py for db queries command

#canteen tables
class Canteen(Base):
    __tablename__ = "canteens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    occupancy = Column(Integer, nullable=False, default=0)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint("occupancy >= 0 AND occupancy <= 100", name="occupancy_percentage"),
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

    queue = Column(Integer, nullable=False, default=0)  # people waiting
    image_url = Column(String(255), nullable=True)

    canteen_id = Column(Integer, ForeignKey("canteens.id"), nullable=False)

    # ORM relationship
    canteen = relationship("Canteen", back_populates="restaurants")