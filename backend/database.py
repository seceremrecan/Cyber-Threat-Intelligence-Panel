from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.models.models import Base
from dotenv import load_dotenv
import os
import logging


load_dotenv()

DB_USER = os.getenv("USER")
DB_PASS = os.getenv("PASSWORD")
DB_HOST = os.getenv("HOST")
DB_NAME = os.getenv("DATABASE")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_specific_ioc_db(ioc: Base, ioc_type: str):
    db = SessionLocal()
    try:
        existing_ioc = db.query(ioc_type).filter(ioc_type.ioc == ioc.ioc).first()
        if existing_ioc:
            return "exists"
        else:
            db.add(ioc)
            db.commit()
            db.refresh(ioc)
            return "created"
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        db.rollback()
        return "error"
    finally:
        db.close()


def get_specific_ioc_db(ioc_value: str, ioc_type: str):
    db = SessionLocal()
    try:
        ioc_instance = db.query(ioc_type).filter(ioc_type.ioc == ioc_value).first()
        return ioc_instance
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
