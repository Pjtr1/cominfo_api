from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:LBdAOcDtaAKqNuEzzwgmauyfpjZBZwoq@hopper.proxy.rlwy.net:22481/railway"
# mysql+pymysql://root:DNQoWUMtELAFdWeoTsRdbfXpqogAKWNN@mainline.proxy.rlwy.net:53907/railway
# first db


#"mysql+pymysql://root:SDNQoWUMtELAFdWeoTsRdbfXpqogAKWNN@mainline.proxy.rlwy.net:53907/railway?ssl=true"   ssl encryption


engine = create_engine(DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {}
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get DB session
#used to be in main, moved here to fix circular import
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()