from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:DNQoWUMtELAFdWeoTsRdbfXpqogAKWNN@mainline.proxy.rlwy.net:53907/railway"

#"mysql+pymysql://root:SDNQoWUMtELAFdWeoTsRdbfXpqogAKWNN@mainline.proxy.rlwy.net:53907/railway?ssl=true" for railway mysql db
#"mysql+pymysql://User1:Simplepassword-123@localhost/compro_app" old one for the local mysql server
#mysql+pymysql://root:yourpassword@localhost/yourdbname
#for others use, if using their own db, change user, password, server, db to theirs
#if using your db change local host to your ip

engine = create_engine(DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {}
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get DB session
#used to be in main.py but caused some circular import so moved here
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()