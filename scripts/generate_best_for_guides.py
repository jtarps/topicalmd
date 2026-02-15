#!/usr/bin/env python3
"""Generate 'Best cream for [condition]' roundup articles and push to Sanity CMS."""

import json
import os
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv
from openai import OpenAI
from slugify import slugify

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

USE_CASES = [
    {
        "condition": "Arthritis",
        "slug": "arthritis",
        "categories": ["arthritis", "joint-pain"],
        "description": "arthritis pain including osteoarthritis, rheumatoid arthritis, and inflammatory joint conditions",
    },
    {
        "condition": "Muscle Pain",
        "slug": "muscle-pain",
        "categories": ["muscle-pain", "sports"],
        "description": "sore muscles, muscle strains, exercise-related soreness, and general muscular pain",
    },
    {
        "condition": "Back Pain",
        "slug": "back-pain",
        "categories": ["back-pain"],
        "description": "lower back pain, upper back pain, sciatica, and chronic back conditions",
    },
    {
        "condition": "Neuropathy",
        "slug": "neuropathy",
        "categories": ["neuropathy", "nerve-pain"],
        "description": "peripheral neuropathy, diabetic nerve pain, and nerve-related pain conditions",
    },
    {
        "condition": "Joint Pain",
        "slug": "joint-pain",
        "categories": ["joint-pain", "arthritis"],
        "description": "general joint pain, stiffness, and inflammation in knees, hips, shoulders, and hands",
    },
    {
        "condition": "Knee Pain",
        "slug": "knee-pain",
        "categories": ["knee-pain", "joint-pain"],
        "description": "knee pain from osteoarthritis, runner's knee, meniscus issues, and general knee discomfort",
    },
    {
        "condition": "Neck & Shoulder Pain",
        "slug": "neck-shoulder-pain",
        "categories": ["neck-pain", "muscle-pain"],
        "description": "neck tension, shoulder stiffness, tech neck, and cervical pain",
    },
    {
        "condition": "Post-Workout Recovery",
        "slug": "post-workout-recovery",
        "categories": ["sports", "muscle-pain"],
        "description": "delayed onset muscle soreness (DOMS), post-exercise recovery, and athletic muscle care",
    },
    {
        "condition": "Plantar Fasciitis",
        "slug": "plantar-fasciitis",
        "categories": ["foot-pain"],
        "description": "plantar fasciitis heel pain, foot arch pain, and inflammatory foot conditions",
    },
    {
        "condition": "Sciatica",
        "slug": "sciatica",
        "categories": ["back-pain", "nerve-pain"],
        "description": "sciatic nerve pain, lower back radiating pain, and piriformis syndrome",
    },
    {
        "condition": "Carpal Tunnel",
        "slug": "carpal-tunnel",
        "categories": ["nerve-pain", "joint-pain"],
        "description": "carpal tunnel syndrome, wrist pain, and repetitive strain injuries",
    },
    {
        "condition": "Sports Injuries",
        "slug": "sports-injuries",
        "categories": ["sports", "muscle-pain"],
        "description": "sprains, strains, bruises, tendonitis, and acute sports-related pain",
    },
]


def load_products():
    with open("data/affiliate_products.json") as f:
        data = json.load(f)
    return data["products"]


def generate_best_for_prompt(use_case, products):
    product_list = "\n".join(
        [f"- {p['product_name']} ({p['brand']}) - {p.get('active_ingredient', 'N/A')}, {p.get('type', 'cream')}, {p.get('price_range', 'N/A')}" for p in products[:8]]
    )
    return f"""You are a medical content writer creating a comprehensive "best of" roundup guide. Write for a health-conscious audience seeking evidence-based recommendations.

Topic: Best Topical Creams for {use_case['condition']}
Target condition: {use_case['description']}

Available products to consider:
{product_list}

Write a comprehensive guide with the following structure:

1. **Title**: "Best Topical Creams for {use_case['condition']} in 2025: Expert Picks"
2. **Introduction** (200 words): Why topical treatments matter for {use_case['condition']}. Briefly explain the condition and how topical treatments help. Cite medical sources (Mayo Clinic, Arthritis Foundation, NIH).
3. **How We Chose** (100 words): Evaluation criteria - ingredient effectiveness, clinical evidence, user reviews, value, ease of use.
4. **Top Picks** (main section): For each recommended product (5-7 products):
   - Product name and brief description
   - Why it made the list
   - Key ingredients and how they work for this condition
   - Best for (specific sub-use case)
   - Price and value assessment
   - Potential downsides
5. **Comparison Table**: Quick-reference table comparing key attributes
6. **How to Choose the Right Cream** (200 words): Factors to consider, ingredient types to look for
7. **How to Use Topical Pain Creams Effectively**: Application tips, frequency, when to see results
8. **When to See a Doctor**: Red flags, signs topical treatment isn't enough
9. **FAQ**: 4-5 frequently asked questions about topical treatments for {use_case['condition']}
10. **Medical Disclaimer**

Include E-E-A-T signals throughout. Mention HSA/FSA eligibility where applicable. Use rel="sponsored" notes for product links. Do NOT fabricate clinical trial data."""


def push_to_sanity(use_case, content, prompt):
    title = f"Best Topical Creams for {use_case['condition']} in 2025: Expert Picks"
    slug = f"best-creams-for-{use_case['slug']}"
    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#") and len(l.strip()) > 30]
    excerpt = lines[0][:300] if lines else f"Our expert picks for the best topical pain relief creams for {use_case['condition']}."

    intro_text = lines[0] if lines else excerpt

    doc = {
        "mutations": [
            {
                "createOrReplace": {
                    "_type": "useCase",
                    "_id": f"usecase-{slug}",
                    "title": title,
                    "slug": {"_type": "slug", "current": slug},
                    "publishedAt": datetime.utcnow().isoformat() + "Z",
                    "excerpt": excerpt,
                    "categories": use_case["categories"],
                    "tags": [use_case["condition"].lower(), "best-for", "roundup", "2025"],
                    "author": "TopicalMD Editorial Team",
                    "metaTitle": f"Best Topical Creams for {use_case['condition']} (2025) | TopicalMD",
                    "metaDescription": excerpt[:160],
                    "introduction": [
                        {
                            "_type": "block",
                            "_key": "intro-0",
                            "style": "normal",
                            "children": [{"_type": "span", "_key": "s-intro-0", "text": intro_text, "marks": []}],
                        }
                    ],
                    "content": [
                        {
                            "_type": "block",
                            "_key": f"block-{i}",
                            "style": "normal",
                            "children": [{"_type": "span", "_key": f"span-{i}", "text": para, "marks": []}],
                        }
                        for i, para in enumerate(content.split("\n\n"))
                        if para.strip()
                    ],
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
    products = load_products()
    max_count = int(sys.argv[1]) if len(sys.argv) > 1 else len(USE_CASES)

    for i, use_case in enumerate(USE_CASES[:max_count]):
        print(f"\n[{i+1}/{max_count}] Generating: Best for {use_case['condition']}")
        relevant = [p for p in products if p.get("category") in use_case["categories"] or p.get("use_case") in [use_case["slug"], use_case["condition"].lower()]]
        if len(relevant) < 3:
            relevant = products[:8]

        try:
            prompt = generate_best_for_prompt(use_case, relevant)
            response = client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.7
            )
            content = response.choices[0].message.content
            push_to_sanity(use_case, content, prompt)
            time.sleep(2)
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nDone! Generated {min(max_count, len(USE_CASES))} best-for guides.")


if __name__ == "__main__":
    main()
