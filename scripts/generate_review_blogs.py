#!/usr/bin/env python3
"""Generate single-product deep-dive review blog posts and push to Sanity CMS."""

import json
import os
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv
from openai import OpenAI
from slugify import slugify

from markdown_to_portable_text import markdown_to_portable_text

load_dotenv()
client = OpenAI()

SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID")
SANITY_DATASET = os.getenv("SANITY_DATASET", "production")
SANITY_TOKEN = os.getenv("SANITY_API_TOKEN")
SANITY_URL = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2025-06-27/data/mutate/{SANITY_DATASET}"
SANITY_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SANITY_TOKEN}",
}


def load_products():
    with open("data/affiliate_products.json") as f:
        data = json.load(f)
    return data["products"]


def generate_review_prompt(product):
    return f"""You are a professional medical writer creating an in-depth product review for a topical pain relief product. Write in a clear, evidence-based tone similar to Healthline or Verywell Health.

Product: {product['product_name']}
Brand: {product['brand']}
Type: {product.get('type', 'cream')}
Active Ingredient: {product.get('active_ingredient', 'N/A')}
Category: {product.get('category', 'general')}
Price Range: {product.get('price_range', 'N/A')}
Size: {product.get('size_g', 'N/A')}g
OTC/Rx: {product.get('otc_rx', 'OTC')}
Mechanism: {product.get('mechanism', 'N/A')}
Notes: {product.get('notes', '')}

Write a comprehensive review with the following structure:

1. **Title** - SEO-optimized review title (e.g., "{product['product_name']} Review: Does It Really Work?")
2. **Summary** - 2-3 sentence overview with a rating out of 5
3. **What Is {product['product_name']}?** - Product overview, what it treats, how it works
4. **Key Ingredients & How They Work** - Scientific explanation of active ingredients. Cite medical sources (Mayo Clinic, PubMed, Arthritis Foundation) where relevant.
5. **How to Use It** - Application instructions, frequency, tips
6. **Who Should Use This Product** - Target conditions, ideal user profile
7. **Who Should Avoid This Product** - Contraindications, drug interactions
8. **Pros** - 4-6 bullet points
9. **Cons** - 3-5 bullet points
10. **Price & Value** - Cost analysis, comparison to alternatives. Mention HSA/FSA eligibility if applicable.
11. **Real User Experiences** - Summarize common feedback themes
12. **Our Verdict** - Final recommendation with rating
13. **FAQ** - 3-4 common questions about this product
14. **Medical Disclaimer** - Standard disclaimer about consulting healthcare providers

Include E-E-A-T signals: cite specific studies or medical guidelines where possible. Use short, scannable paragraphs. Do NOT copy any content from other sites.

FORMATTING: Use standard Markdown throughout: ## for sections, ### for subsections, - for bullet lists, 1. for numbered lists, **bold** for emphasis."""


def extract_title(content):
    for line in content.splitlines():
        cleaned = line.strip().strip("#").strip()
        if cleaned and len(cleaned) > 10:
            cleaned = cleaned.replace("**", "").replace("1.", "").strip()
            if "title" not in cleaned.lower():
                return cleaned
            title_part = cleaned.split(":", 1)
            if len(title_part) > 1:
                return title_part[1].strip().strip('"')
    return None


def extract_rating(content):
    import re

    patterns = [r"(\d\.?\d?)\s*/\s*5", r"rating[:\s]+(\d\.?\d?)", r"(\d\.?\d?)\s*out of\s*5"]
    for pattern in patterns:
        match = re.search(pattern, content.lower())
        if match:
            try:
                return min(float(match.group(1)), 5.0)
            except ValueError:
                pass
    return 4.0


def extract_pros_cons(content):
    pros, cons = [], []
    in_pros, in_cons = False, False
    for line in content.splitlines():
        lower = line.strip().lower()
        if "**pros**" in lower or "## pros" in lower or "### pros" in lower:
            in_pros, in_cons = True, False
            continue
        elif "**cons**" in lower or "## cons" in lower or "### cons" in lower:
            in_pros, in_cons = False, True
            continue
        elif line.strip().startswith(("##", "**")) and ("pros" not in lower and "cons" not in lower):
            in_pros, in_cons = False, False
            continue

        bullet = line.strip().lstrip("-*•").strip()
        if bullet and len(bullet) > 5:
            if in_pros:
                pros.append(bullet)
            elif in_cons:
                cons.append(bullet)
    return pros[:6], cons[:5]


def push_review_to_sanity(product, content, prompt):
    title = extract_title(content) or f"{product['product_name']} Review"
    slug = slugify(title)
    rating = extract_rating(content)
    pros, cons = extract_pros_cons(content)
    product_id = f"product-{slugify(product['product_name'])}"
    excerpt_lines = [
        l.strip()
        for l in content.splitlines()
        if l.strip() and not l.strip().startswith("#") and len(l.strip()) > 30
    ]
    excerpt = excerpt_lines[0][:300] if excerpt_lines else f"A comprehensive review of {product['product_name']}."

    doc = {
        "mutations": [
            {
                "createOrReplace": {
                    "_type": "review",
                    "_id": f"review-{slug}",
                    "title": title,
                    "slug": {"_type": "slug", "current": slug},
                    "publishedAt": datetime.utcnow().isoformat() + "Z",
                    "excerpt": excerpt,
                    "rating": rating,
                    "product": {"_type": "reference", "_ref": product_id},
                    "pros": pros,
                    "cons": cons,
                    "content": markdown_to_portable_text(content),
                    "generatedContent": content,
                    "sourcePrompt": prompt[:500],
                    "sourceModel": "gpt-4o",
                }
            }
        ]
    }

    response = requests.post(SANITY_URL, headers=SANITY_HEADERS, json=doc)
    if response.status_code == 200:
        print(f"  Published review: {title}")
    else:
        print(f"  Failed: {response.text[:200]}")


def main():
    products = load_products()
    category_filter = sys.argv[1] if len(sys.argv) > 1 else None
    max_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    if category_filter:
        products = [p for p in products if p.get("category") == category_filter]
        print(f"Filtered to {len(products)} products in category: {category_filter}")

    count = 0
    for product in products:
        if count >= max_count:
            break
        if product.get("otc_rx") == "Rx":
            continue

        print(f"\n[{count+1}/{max_count}] Generating review for: {product['product_name']}")
        try:
            prompt = generate_review_prompt(product)
            response = client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.7
            )
            content = response.choices[0].message.content
            push_review_to_sanity(product, content, prompt)
            count += 1
            time.sleep(2)
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nDone! Generated {count} reviews.")


if __name__ == "__main__":
    main()
