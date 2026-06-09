"""
Points calculation engine for Wera.

Formula:  Points = (og_price × condition_ratio × wear_ratio) + brand_surplus
"""

CONDITION_RATIO: dict = {
    "Like New": 1.0,
    "Good":     0.75,
    "Fair":     0.5,
}

# How many times the item was worn
WEAR_RATIO: dict = {
    "Barely worn": 1.0,   # 1-5 times
    "Few times":   0.8,   # 6-20 times
    "Regularly":   0.6,   # 21-50 times
    "Well worn":   0.4,   # 50+ times
}

BRAND_SURPLUS: dict = {
    "No brand / Local":      0,
    "H&M / Zara / Mango":   50,
    "Levi's / Tommy / CK":  100,
    "Nike / Adidas / Puma":  80,
    "Luxury Brand":          300,
}

# Exported label lists for UI dropdowns / segmented buttons
WEAR_LABELS  = list(WEAR_RATIO.keys())
BRAND_TIERS  = list(BRAND_SURPLUS.keys())


def calculate_points(og_price: float,
                     condition: str,
                     wear_label: str,
                     brand_tier: str) -> float:
    """Return the computed points value for a listing."""
    cr = CONDITION_RATIO.get(condition,  0.75)
    wr = WEAR_RATIO.get(wear_label,      0.8)
    bs = BRAND_SURPLUS.get(brand_tier,   0)
    return round(og_price * cr * wr + bs, 1)