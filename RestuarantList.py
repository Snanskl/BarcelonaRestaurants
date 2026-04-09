import requests
import time
import json
import csv

api_key = "AIzaSyDRotNWoW4GWNQfTqZNNJ7gepBsRbLFTOM"
url_place = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Barcelona Center LAT & LONG
locations = [
    # Barcelona points
    "41.3851,2.1734",
    "41.3900,2.1600",
    "41.3750,2.1800",
    "41.4000,2.1900",
    
    # Mallorca grid
    "39.9,2.5",
    "39.9,2.8",
    "39.9,3.1",
    "39.6,2.5",
    "39.6,2.8",
    "39.6,3.1",
    "39.3,2.7",
    "39.3,3.0",
    "39.3,3.3"
]

all_places = {}

for loc in locations:
    params = {
        "location": loc,
        "radius": 1500,
        "type": "restaurant",
        "key": api_key
    }

    while True:
        res = requests.get(url_place, params=params).json()

        for place in res.get("results", []):
            all_places[place["place_id"]] = place  # deduplicated by place id

        # Pagination check must be OUTSIDE the for loop!
        if "next_page_token" in res:
            params["pagetoken"] = res["next_page_token"]
            time.sleep(2)  # must wait before using token
        else:
            break

def price_label(level):
    return {1: "€", 2: "€€", 3: "€€€", 4: "€€€€"}.get(level, "N/A")

def get_place_details(place_id, api_key):
    url_detail = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,formatted_address,formatted_phone_number,website,opening_hours",
        "key": api_key
    }
    response = requests.get(url_detail, params=params)
    return response.json()

# Cleaned dataset
data = []
for place_id, p in all_places.items():
    details = get_place_details(place_id, api_key)
    time.sleep(0.1) # 100 milisecond

    result = details.get("result", {})

    if "photos" in p:
        photo_ref = p["photos"][0]["photo_reference"]
        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_ref}&key={api_key}"
    else:
        photo_url = None

    data.append({
        "name": p["name"],
        "rating": p.get("rating"),
        "price": price_label(p.get("price_level")),
        "address": p.get("vicinity"),
        "phone": result.get("formatted_phone_number"),
        "website": result.get("website"),
        "opening_hours": result.get("opening_hours", {}).get("weekday_text", []),
        "photo": photo_url
    })


with open("barcelona_restaurants.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)


with open("barcelona_restaurants.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["name", "rating", "price", "address", "phone", "website", "opening_hours", "photo"])
    writer.writeheader()
    writer.writerows(data)

print(f"Collected {len(data)} restaurants")
