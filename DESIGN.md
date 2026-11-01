# ShopImpact: Design Document (Stages 1 to 4)

## 1. Problem statement

> **At the shelf, a price tag shows one number. The planet's number is missing.**
>
> A shopper can compare two jumpers by price, brand and colour in seconds, yet cannot see that one carries roughly six times the carbon footprint of the other. The seller knows the supply chain, the buyer sees only the price. This **information asymmetry** means that even people who *want* to shop greener are guessing, and guilt-heavy carbon calculators make them feel judged rather than helped.
>
> **ShopImpact** closes that gap *at the moment of decision*. Before the shopper pays, the app attaches a second price tag, the estimated CO₂e, shows what a greener swap would save, and rewards good choices with badges and a friendly turtle guide. The goal is awareness, empowerment and fun, never guilt.

**Goal:** help everyday shoppers see the hidden environmental cost of what they buy and gently motivate them to choose greener options.

## 2. Users and their needs

| Persona | Who | Pain point | What they need |
|---|---|---|---|
| Maya, 19, student | Tight budget, curious, loves thrift | Doesn't know whether her choices matter | Quick numbers, proof that second-hand wins, shareable badges |
| The Rao family | Parents + 2 kids, weekly grocery and home shopping | Overwhelmed by "eco" labels | Simple monthly totals, a clear goal, kid-friendly visuals |
| Sam, 27, young professional | Buys electronics and clothes online | Greenwashing fatigue | Honest comparisons (new vs refurbished), no lecture |

**Empathy map (summary)**
- *Thinks:* "I'd like to help the planet but I don't know what actually matters."
- *Feels:* guilty, confused, sometimes powerless.
- *Says:* "Is this brand actually green?"
- *Does:* decides in seconds, mostly on price.
- **Target emotions for the app:** awareness, empowerment, fun.

**Design principles:** (1) show the number *before* the purchase, (2) always offer a swap, never a scolding, (3) celebrate small wins, (4) large, readable type for everyone.

## 3. Feature plan (mind-map sorted)

| Must-have (compulsory) | Nice-to-have (optional, all built) |
|---|---|
| Input fields: product type, price, brand | Tara the mascot guide with moods and speech bubble |
| Real-time CO₂ estimate (live preview) | Random eco tip after every purchase |
| Monthly dashboard: spend, CO₂, charts | Motivational quotes with "New quote" button |
| Badges (Eco Saver, Low Impact Shopper + 5 more) | High-contrast / larger-text accessibility mode |
| Greener-alternatives list for every product type | Currency selector (USD, INR, EUR, GBP) |
| Turtle graphic on eco-friendly choices | Personal monthly CO₂ goal slider + traffic-light status |
| | "What-if" swap savings and real-world equivalents (km driven, tree-months) |
| | CSV export and import, undo last purchase, demo data |
| | Animated turtle drawings (leaf, badge, footprint, sprout) |

## 4. Visual style

**Palette (pastel earth tones):** beige `#F4F1E8` (background), sage `#7FB08A` (primary), forest `#3F6B4F` (headings), sky `#DCEBF2` (metric cards), sand `#EFE4C8` (badges, bubbles), soft terracotta `#E3B7A0` (ribbons).
**Why:** greens and blues signal nature and calm, beige keeps contrast gentle, and the traffic-light chips (green / amber / red) are softened so "over goal" never feels like an alarm.
**Typography:** 18 px base text (21 px in high-contrast mode), 2.6 rem title, 2.2 rem metric values so the important numbers stand out.

## 5. Wireframe (desktop)

```
+----------------------------------------------------------------------------------+
| SIDEBAR            |  [Tara]   ShopImpact: see the hidden cost before you buy    |
| Tara's tour        |  (mascot) ( Tara says: speech bubble that reacts )          |
| Currency [v]       |----------------------------------------------------------   |
| Monthly goal ----o |  INPUT CARD                                                 |
| High-contrast [ ]  |  [Product type v] [Brand........] [Price] [Date]            |
| [Load demo data]   |  [ ] Certified ethical brand                                |
| [Undo] [Clear]     |  Est. CO2e: 12.4 kg | chip: Green choice | swap saves 5 kg  | 
| [Download CSV]     |  > Greener options (expander)              [ + Log purchase]|
| [Import CSV]       |----------------------------------------------------------   |
|                    |  DASHBOARD (centre)            |  SIDE PANEL                |
|                    |  Month [v]                     |  MY BADGES (grid, locked   |
|                    |  [Spend][CO2][Green %][Count]  |  ones greyed with "how")   |
|                    |  Status banner + progress bar  |  TARA DRAWS (animated      |
|                    |  Tabs: Category | Trend | List |  turtle: leaf/badge/foot)  |
|                    |  (bar charts / table)          |  Eco tip  |  Quote         |
+----------------------------------------------------------------------------------+
```

*(Add your hand-drawn or Canva wireframe photo to `docs/wireframe.png` as well, and reference it in the README.)*

**Mobile:** Streamlit stacks the columns vertically: header, inputs, dashboard, then badges and turtle.

## 6. Python logic design (Stage 2)

**Files:** `data.py` (curated data), `engine.py` (pure logic), `turtle_art.py` (drawings), `mascot.py` (Tara), `app.py` (interface), `tests/` (unit tests).

**Data structures**
- `purchases`: a **list** of **dictionaries** `{date, type, brand, price, currency, ethical, second_life, green, co2}`
- `PRODUCT_TYPES`: a dict of dicts (multiplier, group, swap target, icon)
- `ALTERNATIVES`: dict mapping each type to a **list** of suggestions
- `BADGES` (display) and `BADGE_RULES` (functions) both keyed by badge id

**Calculation rules**
1. `CO₂e (kg) = price × currency→USD rate × product multiplier`
2. If the brand is ethical (ticked or on the curated list): `× 0.85`
3. A product is *eco-tier* if its multiplier ≤ 0.20 kg per USD; a purchase is a *green choice* if it is eco-tier **or** from an ethical brand.
4. Swap saving = footprint now − footprint of the type named in `swap_to`.
5. Equivalents: 0.21 kg CO₂ per km driven; one tree absorbs about 1.75 kg per month (both approximate).

**Badge rules (evaluated for the month of the latest purchase)**

| Badge | Rule |
|---|---|
| First Step | at least 1 purchase logged |
| Footprint Tracker | at least 10 purchases logged |
| Low Impact Shopper | ≥ 3 purchases and month CO₂ ≤ goal |
| Eco Saver of the Month | ≥ 5 purchases, CO₂ ≤ 50% of goal, ≥ 60% green choices |
| Ethical Brand Champion | ≥ 3 ethical-brand purchases in the month |
| Second-Life Hero | ≥ 2 second-hand / refurbished / refill purchases in the month |
| Green Streak | last 3 purchases were all green choices |

**Honesty note:** multipliers are illustrative spend-based estimates built to show *relative* differences between choices. They are not a certified life-cycle assessment.

## 7. Turtle graphics (Stage 3)

Python's `turtle` module draws in a desktop window and needs Tk, which a cloud server does not have. `turtle_art.py` therefore contains an **SVG turtle** with the same commands (`forward`, `left`, `right`, `penup`, `pendown`, `goto`, `circle`, `begin_fill`, `end_fill`). It records every move and plays it back as an animated SVG, so users watch the leaf, badge, footprint or sprout being drawn stroke by stroke.

| Moment | Drawing |
|---|---|
| Nothing logged yet | Sprout in a pot |
| Green choice logged | Leaf |
| New badge earned | Medal (plus balloons) |
| Otherwise | Footprint coloured by monthly status (green / amber / red) |

## 8. Testing (Stage 4)

### 8.1 Automated tests
`python -m unittest discover tests -v` runs 19 tests covering the formula, currency conversion, zero or negative prices, ethical-brand discount, swap savings, monthly totals, empty months, traffic-light status and every badge rule. **All 19 pass.**

### 8.2 Manual test script: 15 purchases (cheap, expensive, eco, non-eco)
Enter these in order (USD) and check the live preview matches the expected value before pressing *Log*.

| # | Product | Brand | Price ($) | Expected kg CO₂e | Green? |
|---|---|---|---|---|---|
| 1 | Fast-fashion clothing | QuickStyle | 45 | 22.5 | No |
| 2 | Second-hand clothing | Thrift (ethical) | 22 | 1.5 | Yes |
| 3 | Leather shoes | StepRight | 120 | 84.0 | No |
| 4 | Recycled-material shoes | Veja (ethical) | 60 | 12.75 | Yes |
| 5 | New electronics | TechNova | 520 | 234.0 | No |
| 6 | Refurbished electronics | ReNew | 80 | 12.0 | Yes |
| 7 | Meat & dairy groceries | Local Mart | 38 | 34.2 | No |
| 8 | Plant-based groceries | GreenBasket | 30 | 6.0 | Yes |
| 9 | Local seasonal produce | Farmers Market (ethical) | 18 | 1.84 | Yes |
| 10 | Packaged snacks | SnackCo | 12 | 4.2 | No |
| 11 | Single-use plastic goods | BulkPack | 9 | 5.4 | No |
| 12 | Reusable household goods | Local Market (ethical) | 15 | 1.27 | Yes |
| 13 | New furniture | FlatHome | 250 | 100.0 | No |
| 14 | Second-hand furniture | Thrift (ethical) | 60 | 3.57 | Yes |
| 15 | Refill / zero-waste cosmetics | The Body Shop (ethical) | 20 | 2.04 | Yes |

**Checks to tick off:** totals update immediately after each log, the progress bar and status change colour as the goal is crossed, *Green Streak* appears after three green choices in a row, *First Step* appears after purchase 1, *Footprint Tracker* after purchase 10, the leaf appears on green purchases and the medal on a new badge, prices of 0 show Tara's friendly error, and *Undo last* and *Clear everything* work.

### 8.3 User feedback log (fill in with YOUR real testers)

| Tester | What confused them / what they said | Change I made |
|---|---|---|
| (name, e.g. friend) | | |
| (name, e.g. parent) | | |
| (name, e.g. sibling) | | |

*Tip: watch quietly while they use the app for two minutes without helping, and write down where they hesitate.*

## 9. Ethical reflection

- **Accuracy and honesty:** CO₂ values are estimates. The app says so on screen and in the README, so it cannot mislead users into thinking it is a certified audit.
- **No guilt, no shaming:** language is encouraging; "over goal" messages stay gentle. Behaviour change lasts longer when it feels good.
- **Greenwashing risk:** ethical-brand status can be self-declared. The checkbox is a trust-based input, and the app asks users to verify claims themselves.
- **Fairness and access:** greener products are sometimes more expensive. The suggestions therefore favour second-hand, repair, refill and library options that save money too. High-contrast mode, large text and currency choice widen access.
- **Privacy:** no login, no tracking, no personal data. Purchases live only in the browser session unless the user downloads a CSV.
- **Societal impact:** the project turns an invisible externality into a visible number, which is the first step towards informed consumer choice. It cannot replace policy or industry change, and it says so.
