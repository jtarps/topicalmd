# Affiliate Products Data

This directory contains the affiliate product mapping file that links products to their affiliate URLs.

## File: `affiliate_products.json`

This JSON file maps product names and brands to affiliate links. The system uses this file to automatically attach affiliate links to products when generating content.

### Structure

```json
{
  "products": [
    {
      "product_name": "Product Name",
      "brand": "Brand Name",
      "affiliate_link": "https://affiliate-link.com/product?ref=YOUR_ID",
      "affiliate_network": "amazon",
      "asin": "B00XXXXXXX",
      "notes": "Optional notes"
    }
  ],
  "matching_rules": {
    "match_by": ["product_name", "brand"],
    "fuzzy_match": true,
    "case_sensitive": false
  }
}
```

### How to Add Affiliate Links

1. **Manual Entry**: Edit `affiliate_products.json` and add your product entries
2. **Programmatic**: Use the `AffiliateProductManager` class in `scripts/affiliate_manager.py`

### Example: Adding a Product

```python
from scripts.affiliate_manager import AffiliateProductManager

manager = AffiliateProductManager()
manager.add_product(
    product_name="Voltaren Arthritis Pain Gel",
    affiliate_link="https://amazon.com/dp/B00XXXXXXX?tag=YOUR_TAG",
    brand="GSK",
    affiliate_network="amazon",
    asin="B00XXXXXXX"
)
```

### Matching Logic

The system matches products using:
- **Product Name**: Primary matching field
- **Brand**: Secondary matching field (helps with disambiguation)
- **Fuzzy Matching**: Enabled by default, allows slight variations in names
- **Threshold**: 0.8 (80% similarity) by default

### Affiliate Networks

Currently supported:
- **Amazon Associates**: Use `asin` field
- **ShareASale**: Use `merchant_id` field
- **Custom**: Direct affiliate links

### Future Enhancements

- API integration for Amazon Associates
- API integration for ShareASale
- Automatic product discovery
- Link validation and health checks

