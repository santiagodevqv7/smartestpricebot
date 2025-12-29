# amazon_utils.py
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def asin_to_title(asin: str) -> str | None:
    url = f"https://www.amazon.com/dp/{asin}"
    r = requests.get(url, headers=HEADERS, timeout=15)

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find(id="productTitle")
    if title:
        return title.text.strip()

    return None
