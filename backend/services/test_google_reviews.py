import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
GOOGLE_PLACE_ID = os.getenv("GOOGLE_PLACE_ID")

url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={GOOGLE_PLACE_ID}&fields=reviews&key={GOOGLE_PLACES_API_KEY}"

response = requests.get(url)

if response.ok:
    reviews = response.json().get('reviews', [])
    print("Google Reviews:", reviews)
else:
    print("Error:", response.status_code, response.text)
