from sqlalchemy.orm import Session
from models import User, Canteen, Restaurant
from passlib.context import CryptContext




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#====================================================================================
#users table
def get_password_hash(password: str):
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, email: str, password: str):
    print("Password before hashing:", password)
    hashed_password = get_password_hash(password)
    db_user = User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

#=========================================================================
#canteen and restaurant tables

def get_all_canteens(db: Session):
    return db.query(Canteen).all()



def get_restaurants_by_canteen(db: Session, canteen_id: int):
    return (
        db.query(Restaurant)
        .filter(Restaurant.canteen_id == canteen_id)
        .all()
    )

