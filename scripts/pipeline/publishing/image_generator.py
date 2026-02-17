"""Image acquisition — fetches product images from Amazon or generates editorial images via DALL-E 3."""

import logging
from typing import Optional

import requests
from openai import OpenAI

from scripts.pipeline.config import (
    DALLE_IMAGE_QUALITY,
    DALLE_IMAGE_SIZE,
    OPENAI_API_KEY,
)
from scripts.pipeline.publishing.sanity_client import upload_image

log = logging.getLogger(__name__)

_oai = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ── DALL-E prompt templates per content type ────────────────────────────────
_DALLE_PROMPTS = {
    "best-for": (
        "A clean, modern medical illustration showing {topic}. "
        "Minimal style, soft blue-green palette, no text, no faces, "
        "suitable as a blog hero image. Professional healthcare aesthetic."
    ),
    "comparison": (
        "A clean split-view product photography layout showing two topical pain relief products "
        "side by side on a white background. Minimal, no text, studio lighting."
    ),
    "faq": (
        "A clean infographic-style illustration representing common questions about {topic}. "
        "Minimal design, question mark motifs, soft pastel medical palette, no text."
    ),
    "review": (
        "A product photography style image of a generic topical pain cream tube "
        "on a clean white background with soft shadows. Studio lighting, minimal."
    ),
}


def fetch_product_image(asin: str) -> Optional[bytes]:
    """Try to download a product image from Amazon using the ASIN.

    Fetches the product page and extracts the Open Graph image URL, then downloads it.
    Returns image bytes or None.
    """
    if not asin:
        return None

    product_url = f"https://www.amazon.com/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html",
    }

    try:
        resp = requests.get(product_url, headers=headers, timeout=10, allow_redirects=True)
        if resp.status_code != 200:
            log.warning("Amazon page returned %d for ASIN %s", resp.status_code, asin)
            return None

        # Extract og:image or main product image from HTML
        import re
        og_match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', resp.text)
        if not og_match:
            # Try the landing image pattern
            og_match = re.search(r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"', resp.text)
        if not og_match:
            og_match = re.search(r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+)"', resp.text)

        if og_match:
            img_url = og_match.group(1)
            img_resp = requests.get(img_url, headers=headers, timeout=10)
            if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                log.info("Fetched product image from Amazon for ASIN %s", asin)
                return img_resp.content

    except requests.RequestException as e:
        log.warning("Failed to fetch Amazon page for ASIN %s: %s", asin, e)

    log.warning("Could not fetch Amazon image for ASIN %s", asin)
    return None


def generate_editorial_image(topic: str, content_type: str) -> Optional[bytes]:
    """Generate an editorial hero image using DALL-E 3. Returns image bytes or None."""
    if not _oai:
        log.warning("OpenAI client not configured — skipping image generation")
        return None

    template = _DALLE_PROMPTS.get(content_type, _DALLE_PROMPTS["best-for"])
    prompt = template.format(topic=topic)

    try:
        response = _oai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=DALLE_IMAGE_SIZE,
            quality=DALLE_IMAGE_QUALITY,
            n=1,
        )
        image_url = response.data[0].url
        img_resp = requests.get(image_url, timeout=30)
        img_resp.raise_for_status()
        log.info("Generated DALL-E image for '%s' (%s)", topic, content_type)
        return img_resp.content
    except Exception as e:
        log.error("DALL-E image generation failed: %s", e)
        return None


def acquire_image(
    topic: str,
    content_type: str,
    asin: Optional[str] = None,
    dry_run: bool = False,
) -> Optional[dict]:
    """Get an image — from Amazon for products, DALL-E for editorial — and upload to Sanity.

    Returns a Sanity image reference dict like {"_type": "image", "asset": {"_type": "reference", "_ref": "image-..."}}
    or None if no image could be acquired.
    """
    image_bytes: Optional[bytes] = None
    filename = "image.jpg"

    # Strategy 1: use product image from Amazon if ASIN is available
    if asin:
        image_bytes = fetch_product_image(asin)
        if image_bytes:
            filename = f"product-{asin}.jpg"

    # Strategy 2: generate editorial image via DALL-E
    if image_bytes is None:
        image_bytes = generate_editorial_image(topic, content_type)
        if image_bytes:
            filename = f"editorial-{content_type}.jpg"

    if image_bytes is None:
        return None

    if dry_run:
        log.info("DRY RUN — would upload %d bytes as %s", len(image_bytes), filename)
        return {"_type": "image", "asset": {"_type": "reference", "_ref": "image-dry-run"}}

    asset_id = upload_image(image_bytes, filename)
    if not asset_id:
        return None

    return {
        "_type": "image",
        "asset": {"_type": "reference", "_ref": asset_id},
    }
