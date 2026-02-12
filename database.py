from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://User1:Simplepassword-123@localhost/compro_app"
#mysql+pymysql://root:yourpassword@localhost/yourdbname
#for others use, if using their own db, change user, password, server, db to theirs
#if using your db change local host to your ip

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
