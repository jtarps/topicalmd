"""Unified Sanity CMS client — query, mutate, and upload assets."""

import logging
from typing import Any, Dict, List, Optional

import requests

from scripts.pipeline.config import (
    SANITY_API_TOKEN,
    SANITY_API_VERSION,
    SANITY_DATASET,
    SANITY_PROJECT_ID,
)

log = logging.getLogger(__name__)

_BASE = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v{SANITY_API_VERSION}"
_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SANITY_API_TOKEN}",
}


def query(groq: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Run a GROQ query and return the result (list or dict)."""
    import json as _json

    url = f"{_BASE}/data/query/{SANITY_DATASET}"
    payload: Dict[str, Any] = {"query": groq}
    if params:
        for k, v in params.items():
            # Sanity expects parameter values to be JSON-encoded
            payload[f"${k}"] = _json.dumps(v)

    resp = requests.get(url, headers=_HEADERS, params=payload, timeout=30)
    resp.raise_for_status()
    return resp.json().get("result", [])


def mutate(mutations: List[Dict], dry_run: bool = False) -> Dict:
    """Send mutations to Sanity. Returns the transaction result."""
    url = f"{_BASE}/data/mutate/{SANITY_DATASET}"
    if dry_run:
        url += "?dryRun=true"

    body = {"mutations": mutations}
    resp = requests.post(url, headers=_HEADERS, json=body, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    log.info("Sanity mutate: %d mutations, dry_run=%s", len(mutations), dry_run)
    return result


def upload_image(image_bytes: bytes, filename: str = "image.jpg") -> Optional[str]:
    """Upload an image to the Sanity assets API and return the asset _id."""
    url = f"{_BASE}/assets/images/{SANITY_DATASET}"
    headers = {
        "Authorization": f"Bearer {SANITY_API_TOKEN}",
        "Content-Type": "image/jpeg",
    }
    resp = requests.post(
        url,
        headers=headers,
        data=image_bytes,
        params={"filename": filename},
        timeout=60,
    )
    resp.raise_for_status()
    doc = resp.json().get("document", {})
    asset_id = doc.get("_id")
    log.info("Uploaded image asset: %s", asset_id)
    return asset_id
