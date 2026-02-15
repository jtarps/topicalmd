#!/usr/bin/env python3
"""
Master content generation runner for TopicalMD.
Orchestrates all content generators in order:
  1. Seed products → 2. Seed ingredients → 3. Reviews → 4. Comparisons → 5. Best-for guides → 6. FAQs
"""

import subprocess
import sys
import time
from datetime import datetime


def run_script(name, script_path, args=None):
    """Run a Python script and return success status."""
    cmd = [sys.executable, script_path] + (args or [])
    print(f"\n{'='*60}")
    print(f"  STEP: {name}")
    print(f"  Script: {script_path}")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"\n  {name} completed successfully.")
            return True
        else:
            print(f"\n  {name} failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"\n  {name} error: {e}")
        return False


def main():
    # Parse arguments
    max_reviews = "5"
    max_comparisons = "5"
    max_best_for = "6"
    max_faqs = "10"
    max_ingredients = "14"
    skip_seeds = False

    for arg in sys.argv[1:]:
        if arg.startswith("--reviews="):
            max_reviews = arg.split("=")[1]
        elif arg.startswith("--comparisons="):
            max_comparisons = arg.split("=")[1]
        elif arg.startswith("--best-for="):
            max_best_for = arg.split("=")[1]
        elif arg.startswith("--faqs="):
            max_faqs = arg.split("=")[1]
        elif arg.startswith("--ingredients="):
            max_ingredients = arg.split("=")[1]
        elif arg == "--skip-seeds":
            skip_seeds = True
        elif arg == "--help":
            print("Usage: python scripts/generate_all.py [options]")
            print("Options:")
            print("  --reviews=N        Max review articles to generate (default: 5)")
            print("  --comparisons=N    Max comparison articles (default: 5)")
            print("  --best-for=N       Max best-for guides (default: 6)")
            print("  --faqs=N           Max FAQ articles (default: 10)")
            print("  --ingredients=N    Max ingredient guides (default: 14)")
            print("  --skip-seeds       Skip product & ingredient seeding")
            return

    start = datetime.now()
    print(f"\nTopicalMD Content Generation Pipeline")
    print(f"Started: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    results = {}

    # Step 1: Seed products
    if not skip_seeds:
        results["Seed Products"] = run_script("Seed Products", "scripts/seed_products.py")
        time.sleep(1)

        # Step 2: Seed ingredients
        results["Seed Ingredients"] = run_script("Seed Ingredients", "scripts/seed_ingredients.py")
        time.sleep(1)

    # Step 3: Generate reviews
    results["Reviews"] = run_script("Generate Reviews", "scripts/generate_review_blogs.py", [max_reviews])
    time.sleep(2)

    # Step 4: Generate comparisons
    results["Comparisons"] = run_script(
        "Generate Comparisons", "scripts/generate_comparison_blogs.py"
    )
    time.sleep(2)

    # Step 5: Generate best-for guides
    results["Best-For Guides"] = run_script(
        "Generate Best-For Guides", "scripts/generate_best_for_guides.py", [max_best_for]
    )
    time.sleep(2)

    # Step 6: Generate ingredient guides
    results["Ingredient Guides"] = run_script(
        "Generate Ingredient Guides", "scripts/generate_ingredient_guides.py", [max_ingredients]
    )
    time.sleep(2)

    # Step 7: Generate FAQs
    results["FAQs"] = run_script("Generate FAQs", "scripts/generate_faqs.py", [max_faqs])

    # Summary
    elapsed = datetime.now() - start
    print(f"\n\n{'='*60}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Total time: {elapsed}")
    print(f"{'='*60}")
    print(f"\nResults:")
    for step, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {step}")

    failed = [s for s, ok in results.items() if not ok]
    if failed:
        print(f"\n{len(failed)} step(s) failed. Check output above for details.")
        sys.exit(1)
    else:
        print("\nAll steps completed successfully!")


if __name__ == "__main__":
    main()
