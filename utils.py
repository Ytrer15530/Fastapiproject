from app import SessionLocal
import requests


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
