from sqlalchemy import Column, Integer, String
from database import Base
#define all tables as class in python using sqlAlchemy, which is basically the core idea of ORM(object relational mapping)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

#"User" class will be primarily used in crud.py for db queries command