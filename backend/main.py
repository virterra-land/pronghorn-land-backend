from fastapi import FastAPI
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'Hello from Pronghorn Land Backend'}

@app.get("/api/testimonials")
def get_testimonials():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM testimonials"))
        testimonials = [dict(row._mapping) for row in result]
        return testimonials
