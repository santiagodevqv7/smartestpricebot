import requests

import os
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def compare_prices(query: str):
    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": SERPAPI_KEY,
        "gl": "us",
        "hl": "en"
    }

    r = requests.get("https://serpapi.com/search", params=params, timeout=20)
    data = r.json()

    offers = []

    for item in data.get("shopping_results", []):
        offers.append({
             "store": item.get("source"),
             "price": parse_price(item.get("price")),
             "link": (
                 item.get("product_link")
                 or item.get("offer_link")
                 or item.get("link")
    ),
    "title": item.get("title")
        })

    return offers

def parse_price(price_str):
    if not price_str:
        return None
    return float(
        price_str
        .replace("$", "")
        .replace(",", "")
        .strip()
    )
