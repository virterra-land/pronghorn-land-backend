import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Always load .env from the backend root, even if script is in services/
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
GOOGLE_PLACE_ID = os.getenv("GOOGLE_PLACE_ID")

def fetch_google_reviews():
    url = f"https://places.googleapis.com/v1/places/{GOOGLE_PLACE_ID}?fields=reviews"
    headers = {
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "reviews"
    }
    resp = requests.get(url, headers=headers)
    data = resp.json()

    # Uncomment to see payload during troubleshooting
    print("DEBUG status:", resp.status_code, "keys:", list(data.keys()))

    reviews = []
    for review in data.get("reviews", []):
        author = (review.get("authorAttribution") or {})
        text = (review.get("text") or {})
        publish_time = review.get("publishTime")  # e.g. 2025-04-18T18:08:36.589481Z
        review_date = (
            datetime.fromisoformat(publish_time.replace("Z", "+00:00")).date()
            if publish_time else None
        )
        reviews.append({
            "reviewer_name": author.get("displayName"),
            "rating": review.get("rating"),
            "review_text": text.get("text"),
            "review_date": review_date,
            "source": "Google",
        })
    return reviews

def ensure_schema():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS testimonials (
            id SERIAL PRIMARY KEY,
            reviewer_name TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            review_text TEXT,
            review_date DATE,
            source TEXT DEFAULT 'Google'
        );
    """)
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS testimonials_unique_review_idx
        ON testimonials (reviewer_name, review_date);
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_reviews(reviews):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    inserted = 0
    for r in reviews:
        cur.execute("""
            INSERT INTO testimonials (reviewer_name, rating, review_text, review_date, source)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (r["reviewer_name"], r["rating"], r["review_text"], r["review_date"], r["source"]))
        inserted += cur.rowcount  # 1 if inserted, 0 if skipped
    conn.commit()
    cur.close()
    conn.close()
    return inserted

if __name__ == "__main__":
    ensure_schema()  # if you added this earlier, keep it here
    reviews = fetch_google_reviews()
    inserted = insert_reviews(reviews)
    print(f"Fetched {len(reviews)}; inserted {inserted}.")

