import re
from urllib.parse import urlparse

def resolve_input(text: str):
    text = text.strip()

    # Keyword
    if not text.startswith("http"):
        return {
            "type": "keyword",
            "store": None,
            "query": text.lower()
        }

    domain = urlparse(text).netloc.lower()

    if "amazon." in domain:
        asin = extract_amazon_asin(text)
        return {
            "type": "link",
            "store": "amazon",
            "query": asin or text
        }

    if "walmart." in domain:
        return {
            "type": "link",
            "store": "walmart",
            "query": clean_slug(text)
        }

    if "bestbuy." in domain:
        return {
            "type": "link",
            "store": "bestbuy",
            "query": clean_slug(text)
        }

    return {
        "type": "link",
        "store": "unknown",
        "query": text
    }


def extract_amazon_asin(url):
    patterns = [
        r"/dp/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})",
        r"/product/([A-Z0-9]{10})"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None



def clean_slug(url):
    path = urlparse(url).path
    slug = path.split("/")[-1]
    return slug.replace("-", " ").lower()
