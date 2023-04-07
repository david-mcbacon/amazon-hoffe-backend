from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(".env")  # server .env


# Connect to the PostgreSQL database
engine = create_engine(
    f'postgresql://{os.environ.get("POSTGRES_USER")}:{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:{os.environ.get("POSTGRES_PORT")}/{os.environ.get("POSTGRES_DB_NAME")}',
    pool_size=20,
    max_overflow=20,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


metadata = MetaData(schema="hoffe_backend")
Base = declarative_base(metadata=metadata)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
