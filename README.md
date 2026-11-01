# 🐢 ShopImpact: Conscious Shopping Dashboard

> **At the shelf, a price tag shows one number. The planet's number is missing.**
> ShopImpact adds a second price tag, the estimated CO₂, *before* you pay, and gently nudges you toward greener choices with a friendly turtle guide named **Tara**.

**🔗 Live app:** `PASTE YOUR STREAMLIT CLOUD LINK HERE`

| | |
|---|---|
| **Student** | `Manya Dhwaneet Mehta`|
|**Student ID**|`2013146`|
| **Candidate registration number** | `100670` |
| **CRS** | Artificial Intelligence |
| **Course** | Python Programming (Summative Assessment, Scenario 1) |
| **School** | `Udgam School for Children `|

![ShopImpact screenshot](docs/screenshot-dashboard.png)
*(Add screenshots to `docs/`: the full dashboard, the input card with live preview, and a turtle drawing.)*

---

## 1. Project overview

**The problem.** Sellers know the supply chain behind a product; shoppers see only a price. This *information asymmetry* leaves even well-meaning people guessing, and guilt-heavy carbon calculators make them feel judged. ShopImpact closes the gap **at the moment of decision**.

**Who it is for.** Young adults, students and eco-conscious families who are curious about their footprint.

**How it feels.** Awareness, empowerment and fun (never guilt): pastel earth tones, large type, live numbers, badges and animated turtle drawings.

The full design thinking (personas, empathy map, wireframes, palette, logic rules, test log, ethics) is in [`docs/DESIGN.md`](docs/DESIGN.md).

## 2. Key features

**Compulsory**
- Input fields for product type, price and brand
- **Real-time CO₂ estimate** as you change any input (before you log it)
- **Monthly dashboard**: total spend, total CO₂, green-choice share, charts by category and by month, full history
- **7 badges**, including *Eco Saver of the Month* and *Low Impact Shopper*
- **Greener alternatives** for every one of the 18 product types, plus "what-if" swap savings
- **Turtle graphics** (leaf, medal, footprint, sprout) drawn stroke by stroke when you make green choices

**Creative extras**
- Mascot **Tara** who reacts to what you do (happy, thinking, cheering)
- Random **eco tip** after every purchase and motivational **quotes**
- **High-contrast / larger-text mode**
- Personal monthly **CO₂ goal** with a traffic-light status and progress bar
- Currency selector (USD, INR, EUR, GBP), CSV export and import, undo, demo data
- Real-world equivalents (km driven, tree-months)

## 3. How it works (logic summary)

```
CO2e (kg) = price x (currency -> USD rate) x product multiplier   [x 0.85 if ethical brand]
```

- `purchases` is a **list of dictionaries**; product multipliers, alternatives and badges are **dictionaries**; badge rules are small **functions** in a dictionary; the app uses loops, conditionals, `datetime` and `pandas.groupby` for the monthly trend.
- Product types with a multiplier ≤ 0.20 are "eco-tier". A purchase is a **green choice** if it is eco-tier or from an ethical brand.
- Multipliers are **illustrative estimates** for awareness and learning, not a certified carbon audit.

## 4. Integration details

| File | Role |
|---|---|
| `app.py` | Streamlit interface: layout, widgets, session state, styling |
| `engine.py` | Pure-Python logic (no Streamlit): calculations, monthly summary, badge rules, swap savings |
| `data.py` | Curated data: multipliers, alternatives, badges, tips, quotes, currencies |
| `turtle_art.py` | Turtle-style SVG drawing engine and the eco drawings |
| `mascot.py` | Tara the Turtle (inline SVG with moods) |
| `tests/test_engine.py` | 19 unit tests for the logic |
| `.streamlit/config.toml` | Pastel theme |
| `requirements.txt` | `streamlit`, `pandas` |

**Why an "SVG turtle"?** Python's built-in `turtle` needs a desktop window (Tk), which cloud servers don't have. `turtle_art.py` reproduces the same commands (`forward`, `left`, `right`, `penup`, `goto`, `circle`, `begin_fill`...) and plays the drawing back as an animation in the browser.

## 5. Run it locally

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
streamlit run app.py
```

Run the tests:

```bash
python -m unittest discover tests -v
```

## 6. Deployment instructions (Streamlit Community Cloud)

1. Push all files to a public GitHub repository (name it like `IDAI102(2013146)-Manya`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **Create app / Deploy an app** → choose your repository, branch `main`, main file `app.py`.
4. Click **Deploy**. When it is live, copy the URL and paste it at the top of this README.
5. Share the repository with **ai.assignments@wacpinternational.org** (Settings → Collaborators).

## 7. How to try it in 60 seconds

1. Open the sidebar and click **Load demo data (15 purchases)**.
2. Watch the dashboard, badges and turtle footprint fill in.
3. Pick *Fast-fashion clothing*, price 50: see the live CO₂ and the swap-to-second-hand saving. Click **Log purchase**.
4. Lower the monthly goal slider to see the traffic-light status change.
5. Switch on **High-contrast mode**.

## 8. Testing and feedback

Automated tests (19, all passing) plus a 15-purchase manual script and a user-feedback log are documented in [`docs/DESIGN.md`](docs/DESIGN.md#8-testing-stage-4).

## 9. Ethics and limitations

Estimates not audits · gentle, guilt-free tone · self-declared "ethical" brands can be greenwashing, so verify · no login, no tracking, no personal data stored · greener options favour ones that also save money. Details in [`docs/DESIGN.md`](docs/DESIGN.md#9-ethical-reflection).

## 10. Future improvements

Barcode scanning, a verified-brand database, per-item lifetime estimates, saved accounts with consent, and sharing badges.
