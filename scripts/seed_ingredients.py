#!/usr/bin/env python3
"""Seed ingredient documents into Sanity CMS.

Creates 14 core Ingredient documents used across topical pain relief products.
Uses the Sanity HTTP Mutations API with createOrReplace for idempotent runs.

Requirements:
    pip install python-slugify python-dotenv requests

Environment variables (via .env):
    SANITY_PROJECT_ID  - Your Sanity project ID
    SANITY_DATASET     - Dataset name (e.g., "production")
    SANITY_API_TOKEN   - API token with write permissions
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from slugify import slugify

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID")
SANITY_DATASET = os.getenv("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.getenv("SANITY_API_TOKEN")
SANITY_API_VERSION = "2024-01-01"

MUTATIONS_URL = (
    f"https://{SANITY_PROJECT_ID}.api.sanity.io"
    f"/v{SANITY_API_VERSION}/data/mutate/{SANITY_DATASET}"
)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SANITY_API_TOKEN}",
}

# ---------------------------------------------------------------------------
# Ingredient Data
# ---------------------------------------------------------------------------

INGREDIENTS = [
    {
        "title": "Diclofenac",
        "scientificName": "Diclofenac sodium",
        "origin": "Synthetic",
        "category": "NSAID",
        "benefits": [
            "Reduces inflammation at the application site",
            "Clinically proven to relieve osteoarthritis pain",
            "Lower systemic absorption than oral NSAIDs",
            "Available in multiple topical formulations (gel, solution, patch)",
        ],
        "sideEffects": [
            "Skin irritation or redness at the application site",
            "Potential photosensitivity — avoid sun exposure on treated skin",
            "Rare risk of gastrointestinal effects with prolonged use",
        ],
        "excerpt": "Diclofenac is a topical NSAID that reduces inflammation and pain directly at the site of application, with significantly lower systemic absorption compared to oral forms.",
        "description": "Diclofenac is a non-steroidal anti-inflammatory drug (NSAID) available in topical gel, solution, and patch formulations. It works by inhibiting cyclooxygenase (COX) enzymes, which are responsible for producing prostaglandins — chemicals that cause inflammation, swelling, and pain. When applied topically, diclofenac penetrates the skin to reach underlying joints and soft tissues, providing localized relief with minimal systemic exposure. It is one of the most well-studied and widely prescribed topical analgesics, with FDA approval for osteoarthritis of joints amenable to topical treatment. The OTC version (Voltaren Arthritis Pain) made topical diclofenac accessible without a prescription in the US in 2020.",
    },
    {
        "title": "Menthol",
        "scientificName": "L-Menthol (C10H20O)",
        "origin": "Derived from mint plants (Mentha arvensis) or synthesized",
        "category": "Counter-irritant",
        "benefits": [
            "Produces immediate cooling sensation that distracts from pain",
            "Activates TRPM8 cold receptors to modulate pain signals",
            "Mild local anesthetic properties",
            "Enhances penetration of other active ingredients",
            "Available in wide range of concentrations (1-16%)",
        ],
        "sideEffects": [
            "Skin irritation in sensitive individuals",
            "Burning or stinging sensation at high concentrations",
            "Should not be applied to broken or damaged skin",
        ],
        "excerpt": "Menthol is a naturally derived counter-irritant that activates cold-sensing receptors in the skin, producing a cooling sensation that helps mask and modulate pain signals.",
        "description": "Menthol is an organic compound obtained from corn mint, peppermint, or synthesized chemically. It is one of the most commonly used active ingredients in topical pain relief products. Menthol works primarily as a counter-irritant — it stimulates the TRPM8 receptors (cold and menthol receptors) in the skin, creating a cooling sensation that effectively distracts the brain from deeper pain signals. At higher concentrations, menthol can also provide mild local anesthetic effects by blocking voltage-gated sodium channels. It is found in gels, creams, patches, and sprays, often combined with methyl salicylate or camphor for dual hot-cold action. Its rapid onset of action makes it one of the most popular OTC topical pain relief ingredients.",
    },
    {
        "title": "Capsaicin",
        "scientificName": "8-Methyl-N-vanillyl-6-nonenamide (C18H27NO3)",
        "origin": "Derived from chili peppers (Capsicum)",
        "category": "TRPV1 agonist",
        "benefits": [
            "Depletes substance P from nerve endings over time, reducing pain transmission",
            "Effective for neuropathic pain conditions",
            "Long-lasting pain relief with consistent use",
            "Available in OTC creams (0.025-0.1%) and prescription patches (8%)",
        ],
        "sideEffects": [
            "Initial burning or stinging sensation (diminishes with repeated use)",
            "Skin redness and warmth at application site",
            "Must avoid contact with eyes, mucous membranes, and open wounds",
            "Requires consistent application for 1-2 weeks for full effect",
        ],
        "excerpt": "Capsaicin is the active compound in chili peppers that works by depleting substance P from nerve endings, gradually reducing pain signal transmission to the brain.",
        "description": "Capsaicin is a naturally occurring compound found in chili peppers of the Capsicum genus. It works by binding to TRPV1 (transient receptor potential vanilloid 1) receptors on sensory nerve fibers. Initial application causes a burning sensation as substance P (a neuropeptide involved in transmitting pain signals) is released. With repeated application, substance P stores become depleted, and the nerve fibers become desensitized, leading to reduced pain perception. This unique mechanism makes capsaicin particularly effective for neuropathic pain, post-herpetic neuralgia, and diabetic peripheral neuropathy. OTC formulations range from 0.025% to 0.1%, while the prescription Qutenza patch delivers a concentrated 8% dose in a single in-clinic application that provides relief for up to three months.",
    },
    {
        "title": "Lidocaine",
        "scientificName": "2-(Diethylamino)-N-(2,6-dimethylphenyl)acetamide",
        "origin": "Synthetic",
        "category": "Local anesthetic",
        "benefits": [
            "Blocks nerve signals at the application site for direct pain relief",
            "Fast-acting numbness within 20-30 minutes",
            "Well-established safety profile",
            "Available in OTC (4%) and prescription (5%) strengths",
        ],
        "sideEffects": [
            "Skin redness or irritation at application site",
            "Temporary numbness extending beyond the target area",
            "Rare allergic reactions (contact dermatitis)",
            "Should not be applied over large body surface areas",
        ],
        "excerpt": "Lidocaine is a local anesthetic that blocks sodium channels in nerve fibers, preventing pain signals from reaching the brain and providing targeted numbing relief.",
        "description": "Lidocaine is a synthetic local anesthetic that works by blocking voltage-gated sodium channels in peripheral nerve fibers. When applied topically, it prevents the initiation and conduction of nerve impulses, effectively numbing the area and stopping pain signals from being transmitted to the brain. Topical lidocaine is available in creams, ointments, and patches. The OTC formulations typically contain 4% lidocaine, while the prescription Lidoderm patch contains 5%. It is particularly useful for post-herpetic neuralgia (shingles pain), localized neuropathic pain, and musculoskeletal pain where numbing the area provides relief. Lidocaine is one of the safest local anesthetics, with minimal systemic absorption when used topically as directed.",
    },
    {
        "title": "Methyl Salicylate",
        "scientificName": "Methyl 2-hydroxybenzoate (C8H8O3)",
        "origin": "Derived from wintergreen (Gaultheria procumbens) or synthesized",
        "category": "Counter-irritant",
        "benefits": [
            "Produces warming sensation that increases blood flow to painful areas",
            "Anti-inflammatory properties as a salicylate derivative",
            "Deep-penetrating relief for muscle and joint pain",
            "Long history of safe and effective OTC use",
        ],
        "sideEffects": [
            "Strong wintergreen odor that some find unpleasant",
            "Skin irritation or allergic reactions in salicylate-sensitive individuals",
            "Must not be used with heating pads or before/after hot showers",
            "Toxic if ingested — keep away from children",
        ],
        "excerpt": "Methyl salicylate is a warming counter-irritant derived from wintergreen that penetrates the skin to increase blood flow and provide anti-inflammatory pain relief.",
        "description": "Methyl salicylate is an organic ester naturally produced by many species of plants, most notably wintergreen. When applied to the skin, it produces a warming sensation by acting as a counter-irritant — stimulating sensory receptors that override and mask deeper pain signals. It also has mild anti-inflammatory properties, as it is metabolized into salicylic acid (the same compound from which aspirin is derived). Methyl salicylate is one of the most widely used ingredients in topical pain relief, found in products like Bengay, IcyHot, and Salonpas. It increases local blood circulation, which helps deliver oxygen and nutrients to damaged tissues while removing waste products. Products containing methyl salicylate should never be used with external heat sources, as this can dramatically increase absorption and risk of toxicity.",
    },
    {
        "title": "Camphor",
        "scientificName": "(1R,4R)-(+)-Camphor (C10H16O)",
        "origin": "Derived from the wood of the camphor tree (Cinnamomum camphora) or synthesized",
        "category": "Counter-irritant",
        "benefits": [
            "Produces both warming and cooling sensations depending on concentration",
            "Mild local anesthetic and anti-itch properties",
            "Increases local blood circulation",
            "Effective in combination with menthol for enhanced pain relief",
        ],
        "sideEffects": [
            "Skin irritation at higher concentrations",
            "Strong distinctive odor",
            "Toxic if ingested — must be kept away from children",
        ],
        "excerpt": "Camphor is a versatile counter-irritant from the camphor tree that produces both warming and cooling sensations while mildly numbing the skin to relieve pain.",
        "description": "Camphor is a waxy, white crystalline substance obtained from the wood of the camphor laurel tree or produced synthetically from turpentine. It has been used medicinally for centuries across Asian and European traditions. As a topical pain reliever, camphor works through multiple mechanisms: it stimulates nerve endings to create a warm-then-cool sensation (counter-irritation), provides mild local anesthetic effects, and increases blood flow to the application area. The FDA classifies camphor as a topical analgesic and anesthetic at concentrations of 3-11%. It is a key ingredient in Tiger Balm, Vicks VapoRub, and many other OTC pain products. Camphor is frequently combined with menthol to create a synergistic cooling-warming effect that many users find particularly effective for muscle soreness.",
    },
    {
        "title": "Trolamine Salicylate",
        "scientificName": "Trolamine salicylate (triethanolamine salicylate)",
        "origin": "Synthetic",
        "category": "Salicylate",
        "benefits": [
            "Provides mild anti-inflammatory pain relief without strong odor",
            "Gentle enough for sensitive skin",
            "Non-greasy and non-staining formulations",
            "Does not produce burning or cooling sensations",
        ],
        "sideEffects": [
            "Less effective than other topical analgesics for moderate-severe pain",
            "Possible allergic reaction in aspirin/salicylate-sensitive individuals",
            "Skin irritation with prolonged use in rare cases",
        ],
        "excerpt": "Trolamine salicylate is a mild topical salicylate analgesic that provides odor-free, gentle pain relief without the intense warming or cooling sensations of other counter-irritants.",
        "description": "Trolamine salicylate is a synthetic salicylate compound used as a topical analgesic. It works by inhibiting prostaglandin synthesis locally, providing mild anti-inflammatory and pain-relieving effects. Unlike methyl salicylate, trolamine salicylate does not produce strong warming or cooling sensations and has minimal odor, making it a preferred choice for people who find menthol- or camphor-based products too intense. It is the active ingredient in the original Aspercreme formula. While it offers gentler relief, some clinical studies have questioned whether it penetrates deeply enough to provide significant anti-inflammatory effects at the joint level. It is best suited for mild arthritis and muscle pain where a no-fuss, no-odor topical is desired.",
    },
    {
        "title": "Arnica Montana",
        "scientificName": "Arnica montana L.",
        "origin": "Flowering plant native to Europe (Asteraceae family)",
        "category": "Natural anti-inflammatory",
        "benefits": [
            "Reduces bruising and swelling from trauma and surgery",
            "Anti-inflammatory properties from sesquiterpene lactones",
            "Well-tolerated with minimal side effects when used topically",
            "Long history in European traditional medicine",
            "Available in both herbal and homeopathic preparations",
        ],
        "sideEffects": [
            "Allergic reactions in people sensitive to Asteraceae/daisy family plants",
            "Should not be applied to broken skin or open wounds",
            "Homeopathic dilutions may have limited clinical evidence",
        ],
        "excerpt": "Arnica montana is a European flowering plant whose extracts contain sesquiterpene lactones that provide natural anti-inflammatory and bruise-healing properties when applied topically.",
        "description": "Arnica montana is a perennial herb native to the mountainous regions of Europe. Its flowers contain sesquiterpene lactones (primarily helenalin), flavonoids, and essential oils that give it anti-inflammatory, analgesic, and anti-ecchymotic (anti-bruising) properties. Topical arnica has been used in European folk medicine for centuries to treat bruises, sprains, and muscle aches. Modern research has shown that arnica extract can inhibit the NF-kB transcription factor, which plays a central role in inflammatory responses. It is available as both concentrated herbal preparations (creams and gels with measurable plant extract) and homeopathic dilutions (which use highly diluted preparations). Boiron's Arnicare and Heel's Traumeel are among the most popular arnica-based topical products. Arnica should only be used on intact skin and never ingested orally in undiluted form.",
    },
    {
        "title": "MSM (Methylsulfonylmethane)",
        "scientificName": "Dimethyl sulfone (C2H6O2S)",
        "origin": "Naturally occurring sulfur compound found in plants, animals, and humans",
        "category": "Sulfur compound",
        "benefits": [
            "Provides bioavailable sulfur important for connective tissue health",
            "Anti-inflammatory properties that may reduce joint swelling",
            "Supports cartilage and collagen integrity",
            "Enhances the effects of other topical analgesic ingredients",
        ],
        "sideEffects": [
            "Mild skin irritation in rare cases",
            "Limited clinical evidence for topical MSM as a standalone treatment",
        ],
        "excerpt": "MSM is a naturally occurring sulfur compound that supports joint and connective tissue health while providing anti-inflammatory benefits when applied topically.",
        "description": "Methylsulfonylmethane (MSM) is an organosulfur compound that occurs naturally in many plants, animals, and the human body. Sulfur is essential for the synthesis of collagen, glucosamine, and chondroitin — all critical building blocks of cartilage, tendons, and ligaments. When used topically, MSM is believed to reduce inflammation by donating sulfur for tissue repair and by modulating inflammatory cytokines. It is commonly included in topical pain relief formulations alongside glucosamine, arnica, or other active ingredients to provide a multi-pathway approach to joint and muscle pain. While more robust clinical evidence exists for oral MSM supplementation, topical formulations benefit from direct delivery to the affected area. Products like Penetrex and Blue-Emu include MSM as a key component of their multi-ingredient formulas.",
    },
    {
        "title": "Glucosamine",
        "scientificName": "2-Amino-2-deoxy-D-glucose (C6H13NO5)",
        "origin": "Natural amino sugar found in shellfish exoskeletons or synthesized",
        "category": "Amino sugar",
        "benefits": [
            "Building block for cartilage repair and maintenance",
            "May slow cartilage degradation in osteoarthritis",
            "Supports joint lubrication and flexibility",
            "Synergistic effects with chondroitin and MSM",
        ],
        "sideEffects": [
            "Possible allergic reaction in shellfish-allergic individuals (shellfish-derived forms)",
            "Limited evidence for topical penetration to joint cartilage",
            "Mild skin irritation in rare cases",
        ],
        "excerpt": "Glucosamine is a natural amino sugar that serves as a building block for cartilage and is used topically to support joint health and repair in arthritis-affected joints.",
        "description": "Glucosamine is an amino sugar that is a key precursor in the biochemical synthesis of glycosylated proteins and lipids that form cartilage, synovial fluid, and other connective tissues. It is most commonly sourced from shellfish shells (glucosamine sulfate or hydrochloride) or produced synthetically for those with shellfish allergies. While oral glucosamine supplements have been widely studied for osteoarthritis (with mixed but generally positive results), topical glucosamine is used in combination products to deliver the compound directly to affected joints. The theory is that topical application allows glucosamine to penetrate the skin and support local cartilage repair, though penetration depth remains debated. It is often paired with MSM, chondroitin, or emu oil in topical formulations like Blue-Emu to provide comprehensive joint support.",
    },
    {
        "title": "CBD (Cannabidiol)",
        "scientificName": "Cannabidiol (C21H30O2)",
        "origin": "Derived from hemp (Cannabis sativa L.)",
        "category": "Cannabinoid",
        "benefits": [
            "Anti-inflammatory effects through interaction with the endocannabinoid system",
            "May reduce pain signaling via CB2 and TRPV1 receptors",
            "Non-psychoactive (does not produce a high)",
            "Anti-oxidant properties that support skin health",
            "Growing body of preclinical evidence for pain relief",
        ],
        "sideEffects": [
            "Regulatory uncertainty — not FDA-approved for topical pain relief",
            "Quality and potency vary significantly between brands",
            "Possible skin irritation or allergic reaction",
            "Full-spectrum products may contain trace THC",
        ],
        "excerpt": "CBD is a non-psychoactive cannabinoid from hemp that interacts with the endocannabinoid system to provide anti-inflammatory and analgesic effects when applied topically.",
        "description": "Cannabidiol (CBD) is one of over 100 cannabinoids found in the Cannabis sativa plant. Unlike THC, CBD does not produce psychoactive effects. When applied topically, CBD interacts with cannabinoid receptors (primarily CB2) in the skin, as well as TRPV1 receptors and other targets involved in pain and inflammation signaling. The skin has its own endocannabinoid system, making it a logical target for topical CBD application. Preclinical studies have shown that CBD has anti-inflammatory, analgesic, and anti-oxidant properties. Topical CBD products come in various forms — creams, balms, roll-ons, and patches — with concentrations typically ranging from 250mg to 3000mg per container. The CBD market lacks FDA regulation for pain claims, so consumers should look for products with third-party lab testing (Certificates of Analysis) and reputable brands like Charlotte's Web, Lazarus Naturals, and Medterra.",
    },
    {
        "title": "Emu Oil",
        "scientificName": "Emu oil (rendered fat of Dromaius novaehollandiae)",
        "origin": "Rendered from the fat of the emu bird",
        "category": "Carrier oil / active",
        "benefits": [
            "Deep skin penetration enhances delivery of other active ingredients",
            "Natural anti-inflammatory properties from omega fatty acids",
            "Moisturizing and skin-conditioning effects",
            "Contains omega-3, omega-6, and omega-9 fatty acids",
        ],
        "sideEffects": [
            "Not suitable for vegans or those with ethical objections to animal-derived products",
            "Rare allergic reactions",
            "Quality varies by refinement and sourcing",
        ],
        "excerpt": "Emu oil is a deeply penetrating carrier oil rich in omega fatty acids that serves both as an anti-inflammatory active ingredient and a penetration enhancer for other compounds.",
        "description": "Emu oil is a bright yellow liquid rendered from the subcutaneous fat of the emu (Dromaius novaehollandiae), a large flightless bird native to Australia. It has been used for thousands of years in Aboriginal Australian medicine for wound healing, skin conditions, and pain relief. Emu oil is composed predominantly of oleic acid (omega-9, ~42%), palmitic acid (~22%), and linoleic acid (omega-6, ~15%), along with smaller amounts of other fatty acids. This fatty acid profile gives it excellent transdermal penetration properties, making it an effective carrier that enhances the absorption of other active ingredients. Research has shown that emu oil itself has anti-inflammatory properties, potentially through inhibition of pro-inflammatory cytokines. It is the signature ingredient in Blue-Emu products and is increasingly used in topical pain formulations as both a functional carrier and an active anti-inflammatory component.",
    },
    {
        "title": "Histamine Dihydrochloride",
        "scientificName": "Histamine dihydrochloride (C5H9N3 \u00b7 2HCl)",
        "origin": "Synthetic",
        "category": "Vasodilator",
        "benefits": [
            "Increases local blood flow to promote healing",
            "Delivers warming sensation without capsaicin or methyl salicylate",
            "Odorless application",
            "Unique mechanism of action distinct from counter-irritants",
        ],
        "sideEffects": [
            "Mild skin redness and warmth at the application site",
            "Not suitable for individuals with histamine sensitivity or mast cell disorders",
            "Less clinical evidence compared to NSAIDs and counter-irritants",
        ],
        "excerpt": "Histamine dihydrochloride is a synthetic vasodilator that increases blood flow to the application site, delivering nutrients and removing pain-causing metabolites for odorless pain relief.",
        "description": "Histamine dihydrochloride is the active ingredient in Australian Dream and related topical pain products. It works as a vasodilator — when applied to the skin, it causes local blood vessels to dilate, increasing blood flow to the area. This enhanced circulation delivers oxygen and nutrients to damaged tissues while removing metabolic waste products that can contribute to pain and inflammation. Unlike most topical analgesics, histamine dihydrochloride does not rely on counter-irritation (cooling or warming sensations) to mask pain. Instead, it aims to address the underlying circulatory component of pain. The product is odorless and non-greasy, making it appealing to people who dislike the strong menthol or wintergreen smells of traditional topical analgesics. It is most commonly used for arthritis and joint pain.",
    },
    {
        "title": "Eucalyptus Oil",
        "scientificName": "Eucalyptus globulus essential oil (primary component: 1,8-cineole / eucalyptol)",
        "origin": "Steam-distilled from leaves of Eucalyptus species",
        "category": "Counter-irritant",
        "benefits": [
            "Cooling and anti-inflammatory sensation on the skin",
            "Contains eucalyptol (1,8-cineole) with proven analgesic properties",
            "Antimicrobial properties that protect injured skin",
            "Enhances absorption of other topical compounds",
            "Aromatherapeutic benefits for relaxation and stress relief",
        ],
        "sideEffects": [
            "Skin irritation or contact dermatitis in sensitive individuals",
            "Strong scent may be overwhelming for some users",
            "Should not be applied near the face of young children",
            "Can cause allergic reactions in eucalyptus-sensitive individuals",
        ],
        "excerpt": "Eucalyptus oil is a cooling essential oil rich in eucalyptol that provides counter-irritant pain relief and anti-inflammatory benefits, with additional antimicrobial properties.",
        "description": "Eucalyptus oil is an essential oil derived from the leaves of Eucalyptus trees, predominantly Eucalyptus globulus and Eucalyptus radiata. Its primary bioactive component is 1,8-cineole (eucalyptol), which typically constitutes 60-90% of the oil. Eucalyptol activates TRPM8 cold receptors (similar to menthol) and has been shown to inhibit pro-inflammatory mediators including TNF-alpha, interleukin-1 beta, and prostaglandin E2. When applied topically, eucalyptus oil produces a cooling sensation and mild local anesthesia while its anti-inflammatory compounds penetrate to underlying tissues. It is used in topical pain products both as a stand-alone active ingredient and as a complementary component that enhances the effects of other analgesics. Eucalyptus oil also has well-documented antimicrobial properties, making it useful in formulations applied to areas where skin integrity may be compromised. It is a common ingredient in natural and organic pain relief balms and liniments.",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def build_portable_text_block(text: str) -> list:
    """Wrap a plain-text paragraph into Sanity Portable Text block format."""
    return [
        {
            "_type": "block",
            "_key": "intro",
            "style": "normal",
            "markDefs": [],
            "children": [
                {
                    "_type": "span",
                    "_key": "span0",
                    "marks": [],
                    "text": text,
                }
            ],
        }
    ]


def build_ingredient_doc(ingredient: dict) -> dict:
    """Build a Sanity Ingredient document from the raw ingredient dict."""
    slug_value = slugify(ingredient["title"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    return {
        "_id": f"ingredient-{slug_value}",
        "_type": "ingredient",
        "title": ingredient["title"],
        "slug": {
            "_type": "slug",
            "current": slug_value,
        },
        "scientificName": ingredient["scientificName"],
        "origin": ingredient["origin"],
        "category": ingredient["category"],
        "benefits": ingredient["benefits"],
        "sideEffects": ingredient["sideEffects"],
        "excerpt": ingredient["excerpt"],
        "publishedAt": now,
        "content": build_portable_text_block(ingredient["description"]),
    }


def send_mutations(mutations: list[dict]) -> dict:
    """Send a batch of mutations to the Sanity Mutations API."""
    payload = {"mutations": mutations}
    response = requests.post(MUTATIONS_URL, headers=HEADERS, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    # Validate environment
    missing = []
    if not SANITY_PROJECT_ID:
        missing.append("SANITY_PROJECT_ID")
    if not SANITY_API_TOKEN:
        missing.append("SANITY_API_TOKEN")
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Set them in your .env file at the project root.")
        sys.exit(1)

    print(f"Seeding {len(INGREDIENTS)} ingredients into Sanity")
    print(f"Target: {SANITY_PROJECT_ID}/{SANITY_DATASET}")
    print("-" * 60)

    mutations = []
    for i, ingredient in enumerate(INGREDIENTS, start=1):
        doc = build_ingredient_doc(ingredient)
        mutations.append({"createOrReplace": doc})
        print(f"  [{i:>2}/{len(INGREDIENTS)}] {ingredient['title']:30s}  ->  {doc['_id']}")

    print("-" * 60)
    print(f"Sending {len(mutations)} mutations to Sanity...")

    try:
        result = send_mutations(mutations)
        tx_id = result.get("transactionId", "unknown")
        results_list = result.get("results", [])
        created = sum(1 for r in results_list if r.get("operation") == "create")
        updated = sum(1 for r in results_list if r.get("operation") == "update")

        print(f"SUCCESS  Transaction: {tx_id}")
        print(f"  Created: {created}  |  Updated: {updated}  |  Total: {len(results_list)}")
    except requests.exceptions.HTTPError as exc:
        print(f"ERROR: Sanity API returned {exc.response.status_code}")
        print(exc.response.text)
        sys.exit(1)
    except requests.exceptions.RequestException as exc:
        print(f"ERROR: Request failed — {exc}")
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
