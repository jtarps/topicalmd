import pandas as pd

"""
NOTE:
This script currently reads comparison data from a local JSON file.
In future versions, product data may come from:
- Google Sheets (via gspread or pandas read_csv from a published link)
- Supabase (via API or Python client)

The JSON structure should remain consistent, containing product_a, product_b, and use_case fields.
"""
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import json
import time
import os
import sys

import requests
from slugify import slugify

# Import affiliate manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from affiliate_manager import AffiliateProductManager

load_dotenv()
client = OpenAI()

# Sanity configuration
SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID")
SANITY_DATASET = os.getenv("SANITY_DATASET", "production")
SANITY_TOKEN = os.getenv("SANITY_API_TOKEN")

SANITY_URL = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2025-06-27/data/mutate/{SANITY_DATASET}"
SANITY_QUERY_URL = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2025-06-27/data/query/{SANITY_DATASET}"
SANITY_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SANITY_TOKEN}"
}

# Initialize affiliate manager
affiliate_manager = AffiliateProductManager("data/affiliate_products.json")

# Set your OpenAI API key here or export it as an environment variable
# openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"

# Load comparison data
filename = "scripts/arthritis_product_comparisons.json"
filename = sys.argv[1] if len(sys.argv) > 1 else "scripts/arthritis_product_comparisons.json"
with open(filename) as f:
    comparisons = json.load(f)

# Function to generate prompt
def generate_comparison_prompt(pair):
    a = pair["product_a"]
    b = pair["product_b"]
    use_case = pair["use_case"].capitalize()

    return f"""You are a professional medical writer creating an informative comparison blog post designed for both human readers and search engine AI systems like Google AI Overview.

Compare two over-the-counter topical pain relief products, using a clear, fact-based tone that prioritizes clarity, accuracy, and reader usability.

Your goal is to help readers quickly understand:
- The main differences between the products
- Who each product is best for
- How they work (mechanism of action)
- Pros and cons of each
- Which one might be better depending on user needs
- Any cost, size, or ingredient differences

Use the following product data as reference for generating the comparison content.

### Product A: {a['product_name']}
- Brand: {a['brand']}
- Form: {a['form']}
- Active Ingredients: {a['active_ingredients']}
- Mechanism: {a['mechanism']}
- Application Type: {a['application_type']}
- OTC/Rx: {a['otc_rx']}
- Generic: {"Yes" if a['is_generic'] else "No"}
- Price: {a['price_range_usd']}
- Size: {a['size_g']}g
- Notes: {a['notes']}

### Product B: {b['product_name']}
- Brand: {b['brand']}
- Form: {b['form']}
- Active Ingredients: {b['active_ingredients']}
- Mechanism: {b['mechanism']}
- Application Type: {b['application_type']}
- OTC/Rx: {b['otc_rx']}
- Generic: {"Yes" if b['is_generic'] else "No"}
- Price: {b['price_range_usd']}
- Size: {b['size_g']}g
- Notes: {b['notes']}

Structure the blog post with the following:
1. Title (clear and SEO-optimized)
2. Introduction (why this comparison matters)
3. Individual Product Overview
4. Comparison Table (if appropriate)
5. Pros and Cons for each
6. Who Each Product is Best For
7. Final Verdict
8. Medical Disclaimer

Use a helpful, unbiased tone similar to Healthline or Verywell Health. Avoid copying the bullet points verbatim. Write short, scannable paragraphs and avoid fluff."""

# Output folder
output_dir = "generated_blogs"
os.makedirs(output_dir, exist_ok=True)
existing_blogs = {f.name for f in Path(output_dir).glob("blog_*.md")}

# Product management functions
def find_or_create_product(product_data, pair_key):
    """
    Find existing product in Sanity or create a new one with affiliate link.
    Returns the product document ID.
    """
    product_name = product_data['product_name']
    brand = product_data.get('brand', '')
    
    # Try to find existing product
    query = f'*[_type == "product" && name == "{product_name}" && brand == "{brand}"][0]'
    query_doc = {
        "query": query
    }
    
    try:
        response = requests.post(SANITY_QUERY_URL, headers=SANITY_HEADERS, json=query_doc)
        if response.status_code == 200:
            result = response.json()
            if result.get('result'):
                product_id = result['result']['_id']
                print(f"  ✓ Found existing product: {product_name}")
                return product_id
    except Exception as e:
        print(f"  ⚠️  Error querying for product: {e}")
    
    # Get affiliate link
    affiliate_info = affiliate_manager.find_affiliate_link(product_name, brand)
    affiliate_link = affiliate_info['affiliate_link'] if affiliate_info else None
    
    if affiliate_link:
        print(f"  ✓ Found affiliate link for {product_name}")
    else:
        print(f"  ⚠️  No affiliate link found for {product_name}")
    
    # Create new product
    product_slug = slugify(product_name)
    product_id = f"product-{product_slug}"
    
    # Extract price from price_range_usd if available
    price = product_data.get('price_range_usd', '')
    
    product_doc = {
        "mutations": [
            {
                "createOrReplace": {
                    "_type": "product",
                    "_id": product_id,
                    "name": product_name,
                    "brand": brand,
                    "form": product_data.get('form', ''),
                    "applicationType": product_data.get('application_type', ''),
                    "price": price,
                    "size": f"{product_data.get('size_g', '')}g" if product_data.get('size_g') else '',
                    "OTC": product_data.get('otc_rx', '').upper() == 'OTC',
                    "isGeneric": product_data.get('is_generic', False),
                    "affiliateLink": affiliate_link,
                    "region": [r.strip() for r in product_data.get('available_in', '').split(',')] if product_data.get('available_in') else []
                }
            }
        ]
    }
    
    try:
        response = requests.post(SANITY_URL, headers=SANITY_HEADERS, json=product_doc)
        if response.status_code == 200:
            print(f"  ✅ Created/updated product: {product_name}")
            return product_id
        else:
            print(f"  ❌ Failed to create product: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Error creating product: {e}")
        return None

# Generate and save blog posts
def push_to_sanity(title, content, slug, prompt, pair):
    lines = content.splitlines()
    
    # Create or find products in Sanity and get their IDs
    print(f"  Creating/finding products in Sanity...")
    product_a_id = find_or_create_product(pair['product_a'], 'product_a')
    product_b_id = find_or_create_product(pair['product_b'], 'product_b')
    
    # Store product data as objects (for comparison table) but also reference product documents
    products = [
        {
            "name": pair['product_a']['product_name'],
            "values": {
                "brand": pair['product_a']['brand'],
                "form": pair['product_a']['form'],
                "active_ingredients": pair['product_a']['active_ingredients'],
                "mechanism": pair['product_a']['mechanism'],
                "application_type": pair['product_a']['application_type'],
                "otc_rx": pair['product_a']['otc_rx'],
                "is_generic": pair['product_a']['is_generic'],
                "price_range_usd": pair['product_a']['price_range_usd'],
                "size_g": pair['product_a']['size_g'],
                "notes": pair['product_a']['notes'],
            },
            "product": {
                "_type": "reference",
                "_ref": product_a_id
            } if product_a_id else None
        },
        {
            "name": pair['product_b']['product_name'],
            "values": {
                "brand": pair['product_b']['brand'],
                "form": pair['product_b']['form'],
                "active_ingredients": pair['product_b']['active_ingredients'],
                "mechanism": pair['product_b']['mechanism'],
                "application_type": pair['product_b']['application_type'],
                "otc_rx": pair['product_b']['otc_rx'],
                "is_generic": pair['product_b']['is_generic'],
                "price_range_usd": pair['product_b']['price_range_usd'],
                "size_g": pair['product_b']['size_g'],
                "notes": pair['product_b']['notes'],
            },
            "product": {
                "_type": "reference",
                "_ref": product_b_id
            } if product_b_id else None
        }
    ]

    doc = {
        "mutations": [
            {
                "createOrReplace": {
                    "_type": "comparison",
                    "_id": f"comparison-{slug}",
                    "title": title,
                    "slug": { "_type": "slug", "current": slug },
                    "excerpt": lines[2].strip() if len(lines) > 2 else "",
                    "introduction": [
                        {
                            "_type": "block",
                            "style": "normal",
                            "children": [
                                {
                                    "_type": "span",
                                    "text": lines[2].strip() if len(lines) > 2 else "",
                                    "marks": []
                                }
                            ]
                        }
                    ],
                    "products": products,
                    "content": [
                        {
                            "_type": "block",
                            "style": "normal",
                            "children": [
                                {
                                    "_type": "span",
                                    "text": content,
                                    "marks": []
                                }
                            ]
                        }
                    ],
                    "sourcePrompt": prompt,
                    "sourceModel": "gpt-4o",
                    "publishedAt": datetime.utcnow().isoformat() + "Z"
                }
            }
        ]
    }

    response = requests.post(SANITY_URL, headers=SANITY_HEADERS, json=doc)
    if response.status_code == 200:
        print(f"✅ Successfully pushed blog to Sanity: {slug}")
    else:
        print(f"❌ Failed to push to Sanity: {response.text}")

blog_count = 0
for i, pair in enumerate(comparisons):
    blog_filename = f"blog_{i+1}.md"
    if blog_filename in existing_blogs:
        print(f"⏩ Skipping {blog_filename}, already exists.")
        continue
    if blog_count >= 10:
        break

    try:
        prompt = generate_comparison_prompt(pair)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        blog_content = response.choices[0].message.content

        with open(f"{output_dir}/{blog_filename}", "w") as f:
            f.write(blog_content)

# inside the for i, pair in enumerate(comparisons) loop

        # Extract title and slug, then push to Sanity
        lines = blog_content.splitlines()
        title_line = next((line for line in lines if line.lower().startswith("1. title:")), "Untitled Blog")
        title = title_line.replace("1. Title:", "").replace("Title:", "").strip().strip('"').strip()
        slug = slugify(title)

        print(f"Pushing: {pair['product_a']['product_name']} vs {pair['product_b']['product_name']}")
        push_to_sanity(title, blog_content, slug, prompt, pair)

        print(f"✅ Blog {i+1} saved.")
        blog_count += 1
        time.sleep(1.5)

    except Exception as e:
        print(f"❌ Error with blog {i+1}: {e}")