#!/usr/bin/env python3
"""Seed product documents into Sanity CMS from affiliate_products.json.

Reads product data from data/affiliate_products.json and creates or updates
Product documents in Sanity CMS using the HTTP Mutations API.

Requirements:
    pip install python-slugify python-dotenv requests

Environment variables (via .env):
    SANITY_PROJECT_ID  - Your Sanity project ID
    SANITY_DATASET     - Dataset name (e.g., "production")
    SANITY_API_TOKEN   - API token with write permissions
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from slugify import slugify

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Load .env from the project root (one level up from scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID")
SANITY_DATASET = os.getenv("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.getenv("SANITY_API_TOKEN")
SANITY_API_VERSION = "2024-01-01"

PRODUCTS_JSON_PATH = PROJECT_ROOT / "data" / "affiliate_products.json"

# Sanity Mutations API endpoint
MUTATIONS_URL = (
    f"https://{SANITY_PROJECT_ID}.api.sanity.io"
    f"/v{SANITY_API_VERSION}/data/mutate/{SANITY_DATASET}"
)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SANITY_API_TOKEN}",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def generate_product_id(product_name: str) -> str:
    """Create a deterministic Sanity document ID from the product name."""
    return f"product-{slugify(product_name)}"


def map_product_to_sanity(product: dict) -> dict:
    """Map a product dict from the JSON file to a Sanity Product document."""
    slug_value = slugify(product["product_name"])

    doc = {
        "_id": generate_product_id(product["product_name"]),
        "_type": "product",
        "name": product["product_name"],
        "slug": {
            "_type": "slug",
            "current": slug_value,
        },
        "brand": product["brand"],
        "form": product["form"],
        "type": product["type"],
        "activeIngredient": product["active_ingredient"],
        "mechanism": product["mechanism"],
        "category": product["category"],
        "useCase": product["use_case"],
        "priceRange": product["price_range"],
        "size": product["size_g"],
        "applicationType": product["application_type"],
        "otcOrRx": product["otc_rx"],
        "isGeneric": product["is_generic"],
        "notes": product["notes"],
        "region": [r.strip() for r in product["available_in"].split(",")],
    }

    # Only set affiliate fields for products that have them
    if product.get("asin"):
        doc["asin"] = product["asin"]
    if product.get("affiliate_url"):
        doc["affiliateLink"] = product["affiliate_url"]

    return doc


def send_mutations(mutations: list[dict]) -> dict:
    """Send a batch of mutations to the Sanity Mutations API."""
    payload = {"mutations": mutations}
    response = requests.post(MUTATIONS_URL, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # Validate environment
    missing = []
    if not SANITY_PROJECT_ID:
        missing.append("SANITY_PROJECT_ID")
    if not SANITY_API_TOKEN:
        missing.append("SANITY_API_TOKEN")
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Set them in your .env file at the project root.")
        sys.exit(1)

    # Load products JSON
    if not PRODUCTS_JSON_PATH.exists():
        print(f"ERROR: Products file not found at {PRODUCTS_JSON_PATH}")
        sys.exit(1)

    with open(PRODUCTS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = data.get("products", [])
    if not products:
        print("No products found in JSON file.")
        sys.exit(1)

    print(f"Found {len(products)} products in {PRODUCTS_JSON_PATH.name}")
    print(f"Target: {SANITY_PROJECT_ID}/{SANITY_DATASET}")
    print("-" * 60)

    # Build mutations — we use createOrReplace so re-running is idempotent
    mutations = []
    for i, product in enumerate(products, start=1):
        doc = map_product_to_sanity(product)
        mutations.append({"createOrReplace": doc})
        print(f"  [{i:>2}/{len(products)}] {product['product_name']}  ->  {doc['_id']}")

    # Send in a single batch (Sanity supports up to ~500 mutations per call)
    print("-" * 60)
    print(f"Sending {len(mutations)} mutations to Sanity...")

    try:
        result = send_mutations(mutations)
        tx_id = result.get("transactionId", "unknown")
        results_list = result.get("results", [])
        created = sum(1 for r in results_list if r.get("operation") == "create")
        updated = sum(1 for r in results_list if r.get("operation") == "update")

        print(f"SUCCESS  Transaction: {tx_id}")
        print(f"  Created: {created}  |  Updated: {updated}  |  Total: {len(results_list)}")
    except requests.exceptions.HTTPError as exc:
        print(f"ERROR: Sanity API returned {exc.response.status_code}")
        print(exc.response.text)
        sys.exit(1)
    except requests.exceptions.RequestException as exc:
        print(f"ERROR: Request failed — {exc}")
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
