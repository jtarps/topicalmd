#!/usr/bin/env python3
"""Generate FAQ content with proper titles and push to Sanity CMS."""

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

FAQ_TOPICS = [
    "What is the strongest over-the-counter pain relief cream?",
    "Can I use topical pain cream with oral pain medication?",
    "How long does topical pain cream take to work?",
    "Are topical pain creams safe for daily use?",
    "What is the difference between cooling and warming pain creams?",
    "Can topical pain creams help with arthritis?",
    "Are natural pain relief creams effective?",
    "What are the side effects of topical pain creams?",
    "Can I use multiple topical pain creams at the same time?",
    "Are topical pain creams better than oral pain medication?",
    "Do topical pain creams work for nerve pain?",
    "Are topical pain creams covered by insurance or HSA/FSA?",
    "What is the best pain cream for knee pain?",
    "How do capsaicin creams work for pain relief?",
    "Can I use topical pain cream during pregnancy?",
    "What is diclofenac gel and how does it compare to ibuprofen?",
    "Do lidocaine patches work for back pain?",
    "What is the best topical treatment for sports injuries?",
    "How do I choose the right topical pain cream?",
    "Can topical creams help with plantar fasciitis?",
]


def generate_faq_prompt(question):
    return f"""You are a medical content writer creating a comprehensive FAQ answer for a topical pain relief information website. Write in a clear, authoritative, evidence-based tone.

Question: {question}

Write a thorough answer that includes:

1. **Direct Answer** (2-3 sentences): Answer the question clearly and directly
2. **Detailed Explanation** (200-400 words): Provide context, scientific backing, and nuance. Cite medical sources (Mayo Clinic, Cleveland Clinic, NIH, PubMed) where applicable.
3. **Key Takeaways**: 3-4 bullet points summarizing the main points
4. **Related Considerations**: Any important caveats, when to see a doctor, or related topics
5. **Sources**: 2-3 real medical sources relevant to this topic (provide source name and general reference)

The answer should be medically accurate, helpful, and optimized for Google's featured snippets. Use short paragraphs and clear headings. Do NOT start with the question repeated."""


def push_faq_to_sanity(question, content, prompt):
    title = question
    slug = slugify(question)[:96]
    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#") and len(l.strip()) > 20]
    excerpt = lines[0][:300] if lines else question

    # Extract sources
    sources = []
    in_sources = False
    for line in content.splitlines():
        lower = line.strip().lower()
        if "source" in lower and ("##" in lower or "**" in lower):
            in_sources = True
            continue
        if in_sources and line.strip().startswith(("-", "*", "•")):
            source_text = line.strip().lstrip("-*•").strip()
            if "http" in source_text:
                parts = source_text.split("http", 1)
                sources.append({"_type": "object", "_key": f"src-{len(sources)}", "title": parts[0].strip().rstrip(":- "), "url": "http" + parts[1].strip().rstrip(")")})
            else:
                sources.append({"_type": "object", "_key": f"src-{len(sources)}", "title": source_text})
        elif in_sources and line.strip().startswith(("##", "**")) and "source" not in lower:
            in_sources = False

    doc = {
        "mutations": [
            {
                "createOrReplace": {
                    "_type": "faq",
                    "_id": f"faq-{slug}",
                    "title": title,
                    "slug": {"_type": "slug", "current": slug},
                    "publishedAt": datetime.utcnow().isoformat() + "Z",
                    "excerpt": excerpt,
                    "answer": [
                        {
                            "_type": "block",
                            "_key": f"block-{i}",
                            "style": "normal",
                            "children": [{"_type": "span", "_key": f"span-{i}", "text": para, "marks": []}],
                        }
                        for i, para in enumerate(content.split("\n\n"))
                        if para.strip()
                    ],
                    "sources": sources[:5] if sources else [],
                }
            }
        ]
    }

    response = requests.post(SANITY_URL, headers=SANITY_HEADERS, json=doc)
    if response.status_code == 200:
        print(f"  Published FAQ: {title[:60]}...")
    else:
        print(f"  Failed: {response.text[:200]}")


def main():
    max_count = int(sys.argv[1]) if len(sys.argv) > 1 else len(FAQ_TOPICS)

    for i, question in enumerate(FAQ_TOPICS[:max_count]):
        print(f"\n[{i+1}/{max_count}] Generating FAQ: {question[:60]}...")
        try:
            prompt = generate_faq_prompt(question)
            response = client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.7
            )
            content = response.choices[0].message.content
            push_faq_to_sanity(question, content, prompt)
            time.sleep(1.5)
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nDone! Generated {min(max_count, len(FAQ_TOPICS))} FAQs.")


if __name__ == "__main__":
    main()
