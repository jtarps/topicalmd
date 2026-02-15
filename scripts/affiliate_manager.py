"""
Affiliate Product Manager

This module handles affiliate product data and matching.
Supports multiple data sources:
1. JSON file (affiliate_products.json) - for manual/managed affiliate links
2. Future: API integrations (Amazon Associates, ShareASale, etc.)
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List
from difflib import SequenceMatcher


class AffiliateProductManager:
    def __init__(self, affiliate_data_path: str = "data/affiliate_products.json"):
        """
        Initialize the Affiliate Product Manager
        
        Args:
            affiliate_data_path: Path to the affiliate products JSON file
        """
        self.affiliate_data_path = affiliate_data_path
        self.affiliate_data = self._load_affiliate_data()
    
    def _load_affiliate_data(self) -> Dict:
        """Load affiliate products data from JSON file"""
        try:
            if os.path.exists(self.affiliate_data_path):
                with open(self.affiliate_data_path, 'r') as f:
                    return json.load(f)
            else:
                # Return empty structure if file doesn't exist
                return {
                    "products": [],
                    "matching_rules": {
                        "match_by": ["product_name", "brand"],
                        "fuzzy_match": True,
                        "case_sensitive": False
                    }
                }
        except Exception as e:
            print(f"⚠️  Warning: Could not load affiliate data: {e}")
            return {"products": [], "matching_rules": {}}
    
    def _fuzzy_match(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def find_affiliate_link(
        self, 
        product_name: str, 
        brand: Optional[str] = None,
        threshold: float = 0.8
    ) -> Optional[Dict]:
        """
        Find affiliate link for a product by matching product name and/or brand
        
        Args:
            product_name: Name of the product to find
            brand: Brand name (optional, helps with matching)
            threshold: Similarity threshold for fuzzy matching (0-1)
        
        Returns:
            Dict with affiliate_link and metadata, or None if not found
        """
        if not self.affiliate_data.get("products"):
            return None
        
        matching_rules = self.affiliate_data.get("matching_rules", {})
        match_by = matching_rules.get("match_by", ["product_name"])
        fuzzy_match = matching_rules.get("fuzzy_match", True)
        case_sensitive = matching_rules.get("case_sensitive", False)
        
        best_match = None
        best_score = 0.0
        
        for product in self.affiliate_data["products"]:
            score = 0.0
            matches = 0
            
            # Match by product name
            if "product_name" in match_by and product.get("product_name"):
                if fuzzy_match:
                    similarity = self._fuzzy_match(
                        product_name, 
                        product["product_name"]
                    )
                    if similarity >= threshold:
                        score += similarity
                        matches += 1
                else:
                    name1 = product_name if case_sensitive else product_name.lower()
                    name2 = product["product_name"] if case_sensitive else product["product_name"].lower()
                    if name1 == name2:
                        score += 1.0
                        matches += 1
            
            # Match by brand
            if "brand" in match_by and brand and product.get("brand"):
                if fuzzy_match:
                    similarity = self._fuzzy_match(brand, product["brand"])
                    if similarity >= threshold:
                        score += similarity * 0.5  # Brand is less important
                        matches += 1
                else:
                    brand1 = brand if case_sensitive else brand.lower()
                    brand2 = product["brand"] if case_sensitive else product["brand"].lower()
                    if brand1 == brand2:
                        score += 0.5
                        matches += 1
            
            # Normalize score
            if matches > 0:
                normalized_score = score / matches
                if normalized_score > best_score:
                    best_score = normalized_score
                    best_match = product
        
        if best_match and best_score >= threshold:
            return {
                "affiliate_link": best_match.get("affiliate_link"),
                "affiliate_network": best_match.get("affiliate_network"),
                "match_score": best_score,
                "metadata": {k: v for k, v in best_match.items() 
                           if k not in ["affiliate_link", "affiliate_network"]}
            }
        
        return None
    
    def get_all_products(self) -> List[Dict]:
        """Get all affiliate products"""
        return self.affiliate_data.get("products", [])
    
    def add_product(
        self, 
        product_name: str,
        affiliate_link: str,
        brand: Optional[str] = None,
        affiliate_network: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Add a new affiliate product to the data file
        
        Args:
            product_name: Name of the product
            affiliate_link: Affiliate link URL
            brand: Brand name (optional)
            affiliate_network: Network name (optional)
            **kwargs: Additional metadata
        
        Returns:
            True if successful, False otherwise
        """
        new_product = {
            "product_name": product_name,
            "affiliate_link": affiliate_link,
            "brand": brand,
            "affiliate_network": affiliate_network or self.affiliate_data.get("default_affiliate_network", "custom"),
            **kwargs
        }
        
        if not self.affiliate_data.get("products"):
            self.affiliate_data["products"] = []
        
        # Check if product already exists
        existing = self.find_affiliate_link(product_name, brand, threshold=0.95)
        if existing:
            print(f"⚠️  Product '{product_name}' already exists. Use update_product() instead.")
            return False
        
        self.affiliate_data["products"].append(new_product)
        return self._save_affiliate_data()
    
    def _save_affiliate_data(self) -> bool:
        """Save affiliate data back to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.affiliate_data_path), exist_ok=True)
            
            with open(self.affiliate_data_path, 'w') as f:
                json.dump(self.affiliate_data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving affiliate data: {e}")
            return False


# Example usage
if __name__ == "__main__":
    manager = AffiliateProductManager()
    
    # Test finding a product
    result = manager.find_affiliate_link(
        "Voltaren Arthritis Pain Gel",
        brand="GSK"
    )
    
    if result:
        print(f"✅ Found affiliate link: {result['affiliate_link']}")
        print(f"   Match score: {result['match_score']:.2f}")
    else:
        print("❌ No affiliate link found")
    
    # Example: Add a new product
    # manager.add_product(
    #     product_name="Test Product",
    #     affiliate_link="https://example.com/product?ref=123",
    #     brand="Test Brand",
    #     affiliate_network="amazon"
    # )

