from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

app = FastAPI()

# Define the data model for form submissions
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str
    website: str = None  # honeypot field, defaults to None

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
    
@app.post("/api/contact")
async def send_contact_form(form_data: ContactForm):
    if form_data.website:
        return {"status": "error", "message": "Spam detected."}

    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO contact_submissions (name, email, message, website)
                    VALUES (:name, :email, :message, :website)
                """),
                {
                    "name": form_data.name,
                    "email": form_data.email,
                    "message": form_data.message,
                    "website": form_data.website
                }
            )
            conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
        return {"status": "error", "message": "Database error occurred."}

    return {"status": "success", "message": "Form received."}


