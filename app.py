"""ShopImpact - the Conscious Shopping Dashboard (main Streamlit app).

Run locally:   streamlit run app.py
Layout (matches the wireframe in docs/DESIGN.md):
    top     -> Tara the mascot + guide bubble, then the purchase input card
    centre  -> monthly dashboard (metrics, charts, history)
    side    -> badges, turtle drawing, eco tip, quote
"""
import random
from datetime import date

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import data
import engine
import turtle_art
from mascot import tara_svg

st.set_page_config(page_title="ShopImpact", page_icon="\U0001F422", layout="wide")


# ===========================================================================
# 1. STATE
# ===========================================================================
def init_state():
    s = st.session_state
    s.setdefault("purchases", [])        # list of purchase dictionaries
    s.setdefault("earned", [])           # badge ids earned so far
    s.setdefault("event", None)          # what happened on the last "Log" click
    s.setdefault("nonce", 0)             # changes on every event -> replays turtle animation
    s.setdefault("tip", random.choice(data.ECO_TIPS))
    s.setdefault("quote", random.choice(data.QUOTES))
    s.setdefault("in_type", list(data.PRODUCT_TYPES)[0])
    s.setdefault("in_brand", "")
    s.setdefault("in_price", 20.0)
    s.setdefault("in_date", date.today())
    s.setdefault("in_ethical", False)
    s.setdefault("currency", "USD ($)")
    s.setdefault("goal", data.DEFAULT_MONTHLY_GOAL_KG)
    s.setdefault("contrast", False)


init_state()
S = st.session_state


def log_purchase():
    """Button callback: store the purchase, update badges, remember what happened."""
    if S.in_price <= 0:
        S.event = {"kind": "error"}
        return
    p = engine.make_purchase(S.in_type, S.in_brand, S.in_price, S.currency, S.in_date, S.in_ethical)
    S.purchases.append(p)
    before = list(S.earned)
    earned_now = engine.evaluate_badges(S.purchases, p["date"].year, p["date"].month, S.goal)
    S.earned = list(dict.fromkeys(before + earned_now))
    swap, saved = engine.swap_saving(p["price"], p["currency"], p["type"], p["ethical"])
    S.nonce += 1
    S.event = {
        "kind": "green" if p["green"] else "regular",
        "co2": p["co2"], "type": p["type"], "brand": p["brand"],
        "swap": swap, "saved": saved,
        "new_badges": engine.new_badges(before, S.earned), "shown": False,
    }
    S.tip = random.choice(data.ECO_TIPS)
    S.view_month = (p["date"].year, p["date"].month)
    S.in_brand, S.in_ethical = "", False
    st.toast("Purchase logged! \U0001F422")


def load_demo():
    S.purchases = engine.demo_purchases()
    today = date.today()
    S.earned = engine.evaluate_badges(S.purchases, today.year, today.month, S.goal)
    S.event, S.nonce = None, S.nonce + 1
    S.view_month = (today.year, today.month)


def clear_all():
    S.purchases, S.earned, S.event = [], [], None
    S.nonce += 1


def undo_last():
    if S.purchases:
        S.purchases.pop()
        S.event = None


# ===========================================================================
# 2. SIDEBAR  (settings, tour, data tools)
# ===========================================================================
with st.sidebar:
    st.markdown("## \U0001F422 Tara's tour")
    st.markdown("**1.** Pick what you plan to buy\n\n**2.** Watch the CO\u2082 estimate update live\n\n"
                "**3.** Log it and collect badges\n\n**4.** Check your monthly dashboard")
    st.divider()
    st.selectbox("Currency", list(data.CURRENCIES), key="currency")
    st.slider("My monthly CO\u2082 goal (kg)", 10, 200, step=5, key="goal",
              help="Badges and the traffic-light status are measured against this goal.")
    st.toggle("High-contrast mode (bigger, bolder)", key="contrast")
    st.divider()
    st.button("\U0001F9EA Load demo data (15 purchases)", on_click=load_demo, width="stretch")
    st.button("\u21A9\uFE0F Undo last purchase", on_click=undo_last, width="stretch")
    st.button("\U0001F5D1\uFE0F Clear everything", on_click=clear_all, width="stretch")
    if S.purchases:
        export = pd.DataFrame(S.purchases)[["date", "type", "brand", "price", "currency", "ethical"]]
        st.download_button("\u2B07\uFE0F Download my purchases (CSV)", export.to_csv(index=False),
                           file_name="shopimpact_purchases.csv", mime="text/csv", width="stretch")
    upload = st.file_uploader("Import a CSV", type="csv", help="Same columns as the download.")
    if upload is not None and st.button("Import file", width="stretch"):
        try:
            frame = pd.read_csv(upload)
            rows = [engine.make_purchase(r["type"], str(r["brand"]) if pd.notna(r["brand"]) else "",
                                         r["price"], r["currency"], pd.to_datetime(r["date"]).date(),
                                         bool(r["ethical"])) for _, r in frame.iterrows()]
            S.purchases.extend(rows)
            st.success(f"Imported {len(rows)} purchases.")
        except Exception:                                   # bad file: stay friendly
            st.error("Sorry, I couldn't read that file. Please use a CSV downloaded from this app.")


# ===========================================================================
# 3. STYLE  (pastel earth tones; high-contrast alternative)
# ===========================================================================
THEMES = {
    "soft": {"bg": "#F4F1E8", "card": "#FFFFFF", "text": "#2F3E36", "head": "#3F6B4F",
             "accent": "#7FB08A", "sky": "#DCEBF2", "sand": "#EFE4C8", "border": "#CFE0CF", "base": "18px"},
    "contrast": {"bg": "#FFFFFF", "card": "#FFFFFF", "text": "#000000", "head": "#0B3D1E",
                 "accent": "#1B7A3A", "sky": "#E6F2FF", "sand": "#FFF4CC", "border": "#000000", "base": "21px"},
}
T = THEMES["contrast" if S.contrast else "soft"]
CSS = """
<style>
 .stApp {background: __bg__; color: __text__;}
 html, body, [class*="css"], .stMarkdown p, label {font-size: __base__ !important; color: __text__;}
 h1 {font-size: 2.6rem !important; color: __head__; letter-spacing: -0.5px;}
 h2, h3 {color: __head__;}
 div[data-testid="stVerticalBlockBorderWrapper"] {background: __card__; border-radius: 18px; border: 2px solid __border__;}
 div[data-testid="stMetric"] {background: __sky__; border-radius: 16px; padding: 12px 16px;}
 div[data-testid="stMetricValue"] {font-size: 2.2rem !important; color: __head__;}
 .stButton > button[kind="primary"] {background: __accent__; border: 0; border-radius: 14px; font-size: 1.15rem; padding: .6rem 1rem; color: #fff; font-weight: 700;}
 .stButton > button {border-radius: 14px;}
 .bubble {background: __sand__; border-radius: 20px; padding: 16px 20px; font-size: 1.15rem; border: 2px solid __border__; position: relative;}
 .bubble:before {content: ""; position: absolute; left: -14px; top: 28px; border: 8px solid transparent; border-right-color: __sand__; border-left: 0;}
 .bob {animation: bob 3s ease-in-out infinite;}
 @keyframes bob {0%,100% {transform: translateY(0);} 50% {transform: translateY(-6px);}}
 .chip {display: inline-block; padding: 6px 14px; border-radius: 999px; font-weight: 700; margin: 2px 0;}
 .chip.good {background: #D5ECD7; color: #1F5B30;} .chip.warn {background: #FBE7C0; color: #7A5200;} .chip.high {background: #F6D5CC; color: #8A3A28;}
 .badge {display: inline-block; width: 46%; margin: 4px 1%; padding: 10px 6px; border-radius: 16px; text-align: center; background: __sand__; border: 2px solid __border__; font-size: .95rem; vertical-align: top;}
 .badge.locked {opacity: .45; filter: grayscale(1);}
 .badge .em {font-size: 2rem; display: block;}
 .status {border-radius: 16px; padding: 14px 18px; font-size: 1.15rem; font-weight: 600; margin: 8px 0;}
 .status.green {background: #D5ECD7; color: #1F5B30;} .status.amber {background: #FBE7C0; color: #7A5200;} .status.red {background: #F6D5CC; color: #8A3A28;}
 .tip {background: __sky__; border-radius: 16px; padding: 12px 16px;}
</style>
"""
for key, value in T.items():
    CSS = CSS.replace(f"__{key}__", value)
st.markdown(CSS, unsafe_allow_html=True)

sym = data.CURRENCIES[S.currency]["symbol"]

# ===========================================================================
# 4. LIVE PREVIEW (computed before drawing, so Tara can react to it)
# ===========================================================================
prev_ethical = engine.is_ethical_brand(S.in_brand, S.in_ethical)
prev_co2 = engine.calculate_impact(S.in_price, S.currency, S.in_type, prev_ethical)
prev_green = engine.is_green_choice(S.in_type, prev_ethical)
prev_swap, prev_saved = engine.swap_saving(S.in_price, S.currency, S.in_type, prev_ethical)


def guide_message():
    """Return (mood, message) for Tara's speech bubble, based on the app state."""
    ev = S.event
    if ev and ev["kind"] == "error":
        return "think", "Hmm, the price needs to be more than zero. Try again?"
    if ev and ev["new_badges"]:
        names = ", ".join(data.BADGES[b]["name"] for b in ev["new_badges"])
        return "cheer", f"WOW! You just earned: {names}! Look at the badge on the right."
    if ev and ev["kind"] == "green":
        return "cheer", f"Green choice! That {ev['type'].lower()} only costs about {ev['co2']} kg CO\u2082e."
    if ev and ev["kind"] == "regular":
        extra = (f" Swapping to {ev['swap'].lower()} next time could save about {ev['saved']} kg. Totally optional!"
                 if ev["swap"] else " Thanks for being honest about it, awareness is step one.")
        return "happy", f"Logged: about {ev['co2']} kg CO\u2082e.{extra}"
    if not S.purchases:
        return "happy", "Hi, I'm Tara! \U0001F422 Choose something you plan to buy below and I'll show its hidden carbon cost, before you pay."
    if prev_green:
        return "cheer", "Ooh, that's a low-impact pick! Log it to see your dashboard grow."
    return "think", "That one has a bigger footprint. Peek at the greener options below. No guilt, just choices!"


# ===========================================================================
# 5. HEADER: Tara + title
# ===========================================================================
mood, message = guide_message()
head_a, head_b = st.columns([1, 4], vertical_alignment="center")
with head_a:
    st.markdown(f'<div class="bob">{tara_svg(mood, 170)}</div>', unsafe_allow_html=True)
with head_b:
    st.markdown("# ShopImpact: see the hidden cost before you buy")
    st.markdown(f'<div class="bubble"><b>Tara says:</b> {message}</div>', unsafe_allow_html=True)

# ===========================================================================
# 6. INPUT CARD (top)
# ===========================================================================
with st.container(border=True):
    st.subheader("\U0001F6D2 What are you planning to buy?")
    c1, c2, c3, c4 = st.columns([2.2, 2, 1.4, 1.4])
    c1.selectbox("Product type", list(data.PRODUCT_TYPES), key="in_type",
                 format_func=lambda k: f"{data.PRODUCT_TYPES[k]['icon']}  {k}")
    c2.text_input("Brand (optional)", key="in_brand", placeholder="e.g. Veja, Thrift, Local Market")
    c3.number_input(f"Price ({sym})", min_value=0.0, step=5.0, format="%.2f", key="in_price")
    c4.date_input("Purchase date", key="in_date")
    st.checkbox("This brand is certified ethical (B Corp, Fair Trade, etc.)", key="in_ethical")

    p1, p2, p3 = st.columns([1.3, 2.2, 1.3], vertical_alignment="center")
    p1.metric("Estimated CO\u2082e", f"{prev_co2} kg")
    with p2:
        if prev_green:
            st.markdown('<span class="chip good">\U0001F33F Green choice</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="chip warn">\U0001F324\uFE0F Higher-impact item</span>', unsafe_allow_html=True)
        eq = engine.equivalents(prev_co2)
        st.caption(f"\u2248 driving {eq['km_driven']} km, or what one tree absorbs in {eq['tree_months']} months (approx.)")
        if prev_swap:
            st.write(f"\U0001F4A1 Swap to **{prev_swap.lower()}** and save about **{prev_saved} kg**.")
    p3.button("\u2795 Log purchase", type="primary", on_click=log_purchase, width="stretch")

    with st.expander(f"\U0001F331 Greener options for {S.in_type.lower()}"):
        for alt in engine.greener_alternatives(S.in_type):
            st.markdown(f"**{alt['name']}**: {alt['why']}")

# celebrations (once per event)
if S.event and S.event.get("new_badges") and not S.event.get("shown"):
    st.balloons()
    S.event["shown"] = True

# ===========================================================================
# 7. MAIN AREA: dashboard (centre) + side panel (badges, turtle)
# ===========================================================================
today = date.today()
months = sorted({(p["date"].year, p["date"].month) for p in S.purchases} | {(today.year, today.month)}, reverse=True)
centre, side = st.columns([2.3, 1])

with centre:
    with st.container(border=True):
        st.subheader("\U0001F4CA Monthly dashboard")
        view = st.selectbox("Month", months, key="view_month",
                            format_func=lambda ym: date(ym[0], ym[1], 1).strftime("%B %Y"))
        summ = engine.monthly_summary(S.purchases, *view)
        spend_local = summ["total_spend_usd"] / data.CURRENCIES[S.currency]["to_usd"]

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total spend", f"{sym}{spend_local:,.0f}")
        m2.metric("Total CO\u2082e", f"{summ['total_co2']} kg")
        m3.metric("Green choices", f"{summ['green_share']}%")
        m4.metric("Purchases", summ["count"])

        if summ["count"] == 0:
            st.markdown('<div class="status amber">\U0001F422 Nothing logged for this month yet. Log a purchase or load the demo data!</div>',
                        unsafe_allow_html=True)
        else:
            status = engine.footprint_status(summ["total_co2"], S.goal)
            words = {"green": "\U0001F33F You're well within your goal. Lovely!",
                     "amber": "\U0001F324\uFE0F Close to your goal. A swap or two will help.",
                     "red": "\U0001F326\uFE0F Over your goal this month. No worries, small swaps add up."}
            st.markdown(f'<div class="status {status}">{words[status]}</div>', unsafe_allow_html=True)
            st.progress(min(summ["total_co2"] / S.goal, 1.0),
                        text=f"{summ['total_co2']} of {S.goal} kg goal used")

            tab1, tab2, tab3 = st.tabs(["By category", "Monthly trend", "All purchases"])
            with tab1:
                cat = pd.Series(summ["by_category"], name="kg CO\u2082e").sort_values(ascending=False)
                st.bar_chart(cat, color="#7FB08A", horizontal=True)
            with tab2:
                frame = pd.DataFrame(S.purchases)
                frame["month"] = pd.to_datetime(frame["date"]).dt.to_period("M").astype(str)
                trend = frame.groupby("month")["co2"].sum().rename("kg CO\u2082e")   # groupby month
                st.bar_chart(trend, color="#8EC5DA")
            with tab3:
                table = pd.DataFrame(S.purchases)[["date", "type", "brand", "price", "currency", "co2", "green"]]
                table.columns = ["Date", "Product", "Brand", "Price", "Currency", "CO\u2082e (kg)", "Green?"]
                st.dataframe(table.sort_values("Date", ascending=False), hide_index=True, width="stretch")

with side:
    with st.container(border=True):
        st.subheader("\U0001F3C5 My badges")
        cards = ""
        for bid, info in data.BADGES.items():
            if bid in S.earned:
                cards += f'<div class="badge"><span class="em">{info["emoji"]}</span><b>{info["name"]}</b></div>'
            else:
                cards += (f'<div class="badge locked" title="{info["how"]}"><span class="em">\U0001F512</span>'
                          f'{info["name"]}<br><small>{info["how"]}</small></div>')
        st.markdown(cards, unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("\U0001F422 Tara draws")
        ev = S.event
        if ev and ev.get("new_badges"):
            art = turtle_art.draw_badge()
            caption = "New badge: " + data.BADGES[ev["new_badges"][0]]["name"]
        elif ev and ev["kind"] == "green":
            art, caption = turtle_art.draw_leaf(), "A leaf for your green choice!"
        elif S.purchases:
            status_now = engine.footprint_status(summ["total_co2"], S.goal) if summ["count"] else "green"
            art = turtle_art.draw_footprint_status(status_now)
            caption = f"Your footprint this month: {status_now}"
        else:
            art, caption = turtle_art.draw_sprout(), "Log a purchase and I'll start drawing!"
        components.html(art.to_html(caption=caption, nonce=S.nonce), height=380)

    st.markdown(f'<div class="tip">\U0001F4A1 <b>Eco tip:</b> {S.tip}</div>', unsafe_allow_html=True)
    st.markdown("")
    st.markdown(f'<div class="tip" style="background:{T["sand"]}">\u201C{S.quote}\u201D</div>', unsafe_allow_html=True)
    st.button("\U0001F501 New quote", on_click=lambda: S.update(quote=random.choice(data.QUOTES)))

st.caption("CO\u2082 values are illustrative estimates for learning and awareness, not a certified carbon audit.")
