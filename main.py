from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import crud
import schemas
from fastapi.middleware.cors import CORSMiddleware

from routes.ai import router as ai_router
from database import get_db

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



@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db, user.email, user.password)
#user after def register is a variable with class of usercreate. the variable is created in that line, user.email is just the email str object in the UserCreate class(see schemas.py)


@app.post("/login", response_model=schemas.UserResponse)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return db_user


#start the server(for testing, will use gunicorn+uvicorn for the actual app)
#remove later
import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

