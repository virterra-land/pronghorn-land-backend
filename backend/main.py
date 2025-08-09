from fastapi import FastAPI
from fastapi.responses import JSONResponse
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

# @app.get("/api/testimonials")
# def get_testimonials():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT reviewer_name, review_text, rating FROM testimonials"))
#         testimonials = [
#             {
#                 "author": row.reviewer_name,
#                 "content": row.review_text,
#                 "rating": row.rating
#             }
#             for row in result
#         ]
#         return testimonials
    
@app.get("/api/testimonials")
def get_testimonials():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT reviewer_name, review_text, rating FROM testimonials WHERE rating >= :min_rating"),
            {"min_rating": 4}
        )
        testimonials = [
            {
                "author": row.reviewer_name,
                "content": row.review_text,
                "rating": row.rating
            }
            for row in result
        ]
        return testimonials


