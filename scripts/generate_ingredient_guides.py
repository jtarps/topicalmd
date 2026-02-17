#!/usr/bin/env python3
"""Generate educational ingredient guide content and push to Sanity CMS."""

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

INGREDIENTS = [
    {"name": "Diclofenac", "scientific": "Diclofenac sodium", "category": "NSAID", "origin": "Synthetic"},
    {"name": "Menthol", "scientific": "L-Menthol", "category": "Counter-irritant", "origin": "Derived from mint (Mentha)"},
    {"name": "Capsaicin", "scientific": "8-Methyl-N-vanillyl-6-nonenamide", "category": "TRPV1 agonist", "origin": "Chili peppers (Capsicum)"},
    {"name": "Lidocaine", "scientific": "Lidocaine hydrochloride", "category": "Local anesthetic", "origin": "Synthetic"},
    {"name": "Methyl Salicylate", "scientific": "Methyl 2-hydroxybenzoate", "category": "Counter-irritant", "origin": "Wintergreen oil"},
    {"name": "Camphor", "scientific": "1,7,7-Trimethylbicyclo[2.2.1]heptan-2-one", "category": "Counter-irritant", "origin": "Camphor tree (Cinnamomum camphora)"},
    {"name": "Trolamine Salicylate", "scientific": "Triethanolamine salicylate", "category": "Salicylate", "origin": "Synthetic"},
    {"name": "Arnica Montana", "scientific": "Arnica montana L.", "category": "Natural anti-inflammatory", "origin": "Arnica flower (Asteraceae)"},
    {"name": "MSM", "scientific": "Methylsulfonylmethane", "category": "Sulfur compound", "origin": "Natural / synthetic"},
    {"name": "Glucosamine", "scientific": "2-Amino-2-deoxy-D-glucose", "category": "Amino sugar", "origin": "Shellfish / synthetic"},
    {"name": "CBD", "scientific": "Cannabidiol", "category": "Cannabinoid", "origin": "Hemp (Cannabis sativa)"},
    {"name": "Emu Oil", "scientific": "Dromiceius oil", "category": "Carrier / anti-inflammatory", "origin": "Emu (Dromaius novaehollandiae)"},
    {"name": "Histamine Dihydrochloride", "scientific": "2-(1H-Imidazol-4-yl)ethanamine dihydrochloride", "category": "Vasodilator", "origin": "Synthetic"},
    {"name": "Eucalyptus Oil", "scientific": "Eucalyptus globulus oil", "category": "Counter-irritant", "origin": "Eucalyptus tree"},
]


def generate_ingredient_prompt(ingredient):
    return f"""You are a medical science writer creating an educational guide about an active ingredient used in topical pain relief products. Write for a general audience with medical accuracy.

Ingredient: {ingredient['name']}
Scientific Name: {ingredient['scientific']}
Category: {ingredient['category']}
Origin: {ingredient['origin']}

Write a comprehensive ingredient guide with:

1. **Title**: "{ingredient['name']} for Pain Relief: What You Need to Know"
2. **Overview** (150 words): What it is, where it comes from, how it's used in topical treatments
3. **How It Works**: Scientific mechanism of action explained in plain language. Cite relevant research (PubMed, clinical trials).
4. **Evidence & Research**: Key clinical studies, FDA status, level of scientific support
5. **Common Products Containing {ingredient['name']}**: Types of products that use this ingredient
6. **Benefits**: 4-6 specific benefits for pain relief
7. **Side Effects & Precautions**: Known side effects, who should avoid it, drug interactions
8. **How to Use Products With {ingredient['name']}**: Application tips, dosing guidance
9. **Comparison to Other Ingredients**: How it compares to alternatives in the same category
10. **FAQ**: 3-4 common questions

Be evidence-based and cite medical sources. Include E-E-A-T signals. Avoid health claims that aren't supported by evidence.

FORMATTING: Use standard Markdown throughout: ## for sections, ### for subsections, - for bullet lists, 1. for numbered lists, **bold** for emphasis."""


def push_ingredient_to_sanity(ingredient, content, prompt):
    title = f"{ingredient['name']} for Pain Relief: What You Need to Know"
    slug = slugify(ingredient["name"])

    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#") and len(l.strip()) > 20]
    excerpt = lines[0][:300] if lines else f"Learn about {ingredient['name']} and how it works for topical pain relief."

    doc = {
        "mutations": [
            {
                "createOrReplace": {
                    "_type": "ingredient",
                    "_id": f"ingredient-{slug}",
                    "title": ingredient["name"],
                    "slug": {"_type": "slug", "current": slug},
                    "publishedAt": datetime.utcnow().isoformat() + "Z",
                    "excerpt": excerpt,
                    "scientificName": ingredient["scientific"],
                    "origin": ingredient["origin"],
                    "category": ingredient["category"],
                    "benefits": [],
                    "sideEffects": [],
                    "content": markdown_to_portable_text(content),
                }
            }
        ]
    }

    response = requests.post(SANITY_URL, headers=SANITY_HEADERS, json=doc)
    if response.status_code == 200:
        print(f"  Published: {title}")
    else:
        print(f"  Failed: {response.text[:200]}")


def main():
    max_count = int(sys.argv[1]) if len(sys.argv) > 1 else len(INGREDIENTS)

    for i, ingredient in enumerate(INGREDIENTS[:max_count]):
        print(f"\n[{i+1}/{max_count}] Generating guide for: {ingredient['name']}")
        try:
            prompt = generate_ingredient_prompt(ingredient)
            response = client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.7
            )
            content = response.choices[0].message.content
            push_ingredient_to_sanity(ingredient, content, prompt)
            time.sleep(2)
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nDone! Generated {min(max_count, len(INGREDIENTS))} ingredient guides.")


if __name__ == "__main__":
    main()
