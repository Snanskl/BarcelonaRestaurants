import requests
import time
import json
import csv

api_key = "AIzaSyDRotNWoW4GWNQfTqZNNJ7gepBsRbLFTOM"
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Barcelona Center LAT & LONG
locations = [
    "41.3851,2.1734",  # city center
    "41.3900,2.1600",  # near Gothic Quarter
    "41.3750,2.1800",  # near Sants
    "41.4000,2.1900"   # near Gràcia
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
        res = requests.get(url, params=params).json()

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

# Cleaned dataset
data = []
for p in all_places.values():
    data.append({
        "name": p["name"],
        "rating": p.get("rating"),
        "price": price_label(p.get("price_level")),
        "address": p.get("vicinity")
    })


with open("barcelona_restaurants.json") as f:
    data = json.load(f)


with open("barcelona_restaurants.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["name", "rating", "price", "address"])
    writer.writeheader()
    writer.writerows(data)

print(f"Collected {len(data)} restaurants")