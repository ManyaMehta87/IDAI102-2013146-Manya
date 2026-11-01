"""engine.py - the "brain" of ShopImpact.

Pure Python (lists, dicts, control structures, datetime). It never imports
Streamlit, so every function can be unit-tested on its own.

Core idea:  CO2 estimate (kg) = price in USD x product multiplier
            (x 0.85 if the brand is ethical)
"""
from collections import defaultdict
from datetime import date

import data


# ---------------------------------------------------------------------------
# Impact calculation
# ---------------------------------------------------------------------------
def to_usd(price, currency):
    """Convert a price in the chosen currency to USD (multipliers are per USD)."""
    return price * data.CURRENCIES[currency]["to_usd"]


def is_ethical_brand(brand, ticked=False):
    """A brand is ethical if the user ticked the box or it is on our curated list."""
    if ticked:
        return True
    return brand.strip().lower() in data.ETHICAL_BRANDS


def calculate_impact(price, currency, product_type, ethical=False):
    """Return the estimated CO2e in kg for one purchase."""
    if price <= 0:
        return 0.0
    multiplier = data.PRODUCT_TYPES[product_type]["multiplier"]
    co2 = to_usd(price, currency) * multiplier
    if ethical:
        co2 *= data.ETHICAL_BRAND_FACTOR
    return round(co2, 2)


def is_eco_tier(product_type):
    """True when the product type itself is a low-impact kind of item."""
    return data.PRODUCT_TYPES[product_type]["multiplier"] <= data.ECO_THRESHOLD


def is_green_choice(product_type, ethical):
    """A green choice = low-impact product type OR an ethical brand."""
    return is_eco_tier(product_type) or ethical


def make_purchase(product_type, brand, price, currency, purchase_date=None, ethical_ticked=False):
    """Build one purchase record (a dictionary) ready to store in the list."""
    brand = brand.strip() or "Unbranded / local"
    ethical = is_ethical_brand(brand, ethical_ticked)
    return {
        "date": purchase_date or date.today(),
        "type": product_type,
        "brand": brand,
        "price": round(float(price), 2),
        "currency": currency,
        "ethical": ethical,
        "second_life": data.PRODUCT_TYPES[product_type]["second_life"],
        "green": is_green_choice(product_type, ethical),
        "co2": calculate_impact(price, currency, product_type, ethical),
    }


# ---------------------------------------------------------------------------
# Suggestions and what-if savings
# ---------------------------------------------------------------------------
def greener_alternatives(product_type):
    """The list of suggestion dictionaries for a product type."""
    return data.ALTERNATIVES.get(product_type, [])


def swap_saving(price, currency, product_type, ethical=False):
    """If a greener type exists, return (swap_type, kg_saved); else (None, 0)."""
    swap = data.PRODUCT_TYPES[product_type]["swap_to"]
    if swap is None:
        return None, 0.0
    now = calculate_impact(price, currency, product_type, ethical)
    then = calculate_impact(price, currency, swap, ethical)
    return swap, round(max(now - then, 0.0), 2)


def equivalents(kg):
    """Friendly real-world comparisons (approximate)."""
    return {
        "km_driven": round(kg / data.KG_CO2_PER_KM_DRIVEN),
        "tree_months": round(kg / data.KG_CO2_ABSORBED_PER_TREE_PER_MONTH, 1),
    }


# ---------------------------------------------------------------------------
# Monthly summary
# ---------------------------------------------------------------------------
def purchases_in_month(purchases, year, month):
    return [p for p in purchases if p["date"].year == year and p["date"].month == month]


def monthly_summary(purchases, year, month):
    """Totals for one month. Spend is converted to USD so currencies can mix."""
    items = purchases_in_month(purchases, year, month)
    by_category = defaultdict(float)
    total_co2 = 0.0
    total_spend_usd = 0.0
    for p in items:                                    # control structure: loop
        total_co2 += p["co2"]
        total_spend_usd += to_usd(p["price"], p["currency"])
        by_category[p["type"]] += p["co2"]
    count = len(items)
    green = sum(1 for p in items if p["green"])
    return {
        "count": count,
        "total_co2": round(total_co2, 2),
        "total_spend_usd": round(total_spend_usd, 2),
        "avg_co2": round(total_co2 / count, 2) if count else 0.0,
        "green_share": round(100 * green / count) if count else 0,
        "ethical_count": sum(1 for p in items if p["ethical"]),
        "second_life_count": sum(1 for p in items if p["second_life"]),
        "by_category": dict(by_category),
    }


def footprint_status(total_co2, goal):
    """Traffic-light status of the month: 'green', 'amber' or 'red'."""
    if goal <= 0:
        return "amber"
    ratio = total_co2 / goal
    if ratio <= 0.75:
        return "green"
    if ratio <= 1.0:
        return "amber"
    return "red"


# ---------------------------------------------------------------------------
# Badge rules: one small function per badge, stored in a dictionary.
# Every rule receives (purchases, summary_for_selected_month, monthly_goal).
# ---------------------------------------------------------------------------
def _rule_first_step(purchases, s, goal):
    return len(purchases) >= 1


def _rule_tracker(purchases, s, goal):
    return len(purchases) >= 10


def _rule_low_impact(purchases, s, goal):
    return s["count"] >= 3 and s["total_co2"] <= goal


def _rule_eco_saver(purchases, s, goal):
    return s["count"] >= 5 and s["total_co2"] <= 0.5 * goal and s["green_share"] >= 60


def _rule_ethical(purchases, s, goal):
    return s["ethical_count"] >= 3


def _rule_second_life(purchases, s, goal):
    return s["second_life_count"] >= 2


def _rule_green_streak(purchases, s, goal):
    ordered = sorted(purchases, key=lambda p: p["date"])   # latest last
    last_three = ordered[-3:]
    return len(last_three) == 3 and all(p["green"] for p in last_three)


BADGE_RULES = {
    "first_step": _rule_first_step,
    "tracker": _rule_tracker,
    "low_impact": _rule_low_impact,
    "eco_saver": _rule_eco_saver,
    "ethical": _rule_ethical,
    "second_life": _rule_second_life,
    "green_streak": _rule_green_streak,
}


def evaluate_badges(purchases, year, month, goal):
    """Return the list of badge ids currently earned."""
    summary = monthly_summary(purchases, year, month)
    return [badge_id for badge_id, rule in BADGE_RULES.items() if rule(purchases, summary, goal)]


def new_badges(before, after):
    """Badge ids that are in `after` but were not in `before`."""
    return [b for b in after if b not in before]


# ---------------------------------------------------------------------------
# Demo data used for testing / marking
# ---------------------------------------------------------------------------
def demo_purchases(today=None):
    """15 realistic purchases (cheap/expensive, eco/non-eco) over two months."""
    today = today or date.today()
    this_month = today.replace(day=1)
    last_month = (this_month.replace(day=1) - (date.resolution)).replace(day=1)
    rows = [
        # (month_anchor, day, type, brand, price, ethical)
        (last_month, 3, "Fast-fashion clothing", "QuickStyle", 45, False),
        (last_month, 6, "Meat & dairy groceries", "Local Mart", 38, False),
        (last_month, 9, "New electronics", "TechNova", 520, False),
        (last_month, 14, "Leather shoes", "StepRight", 120, False),
        (last_month, 20, "Packaged snacks", "SnackCo", 12, False),
        (last_month, 25, "Second-hand books", "Oxfam", 9, True),
        (this_month, 1, "Second-hand clothing", "Thrift", 22, True),
        (this_month, 2, "Local seasonal produce", "Farmers Market", 18, True),
        (this_month, 3, "Plant-based groceries", "GreenBasket", 30, False),
        (this_month, 4, "Refurbished electronics", "ReNew", 80, False),
        (this_month, 5, "Reusable household goods", "Local Market", 15, True),
        (this_month, 6, "Recycled-material shoes", "Veja", 60, True),
        (this_month, 7, "Refill / zero-waste cosmetics", "The Body Shop", 20, True),
        (this_month, 8, "Second-hand furniture", "Thrift", 60, True),
        (this_month, 9, "Local seasonal produce", "Farmers Market", 14, True),
    ]
    out = []
    for anchor, day, ptype, brand, price, ethical in rows:
        d = anchor.replace(day=min(day, 28))
        out.append(make_purchase(ptype, brand, price, "USD ($)", d, ethical))
    return out
