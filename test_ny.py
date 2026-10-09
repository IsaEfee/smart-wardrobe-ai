import sys
import streamlit as st
class Dummy: pass
st.session_state = {'lang': 'tr', 'ml_gender': 'Male', 'ml_profile': 'Standard', 'onboarding_complete': True}

from app import kiyafet_db, generate_outfit, fmt, t, lang

owned_tops = []
for x in kiyafet_db["top_inner"]:
    if x["en"] in ["Short Sleeve T-Shirt", "Shirt", "Thin Knit Sweater", "Hoodie"]:
        owned_tops.append(fmt(x, lang))
for x in kiyafet_db["top_outer"]:
    if x["en"] in ["Thin Windbreaker", "Cardigan", "Winter Puffer Jacket"]:
        owned_tops.append(fmt(x, lang))
owned_tops.append(fmt(next(x for x in kiyafet_db["top_outer"] if x["en"] == "None (Innerwear Only)"), lang))

owned_bots = []
for x in kiyafet_db["bottom_outer"]:
    if x["en"] in ["Jeans", "Sweatpants", "Shorts"]:
        owned_bots.append(fmt(x, lang))
owned_bots.append(fmt(next(x for x in kiyafet_db["bottom_inner"] if x["en"] == "None (Underwear Only)"), lang))

ok, out = generate_outfit(23.2, "Clear", 27.8, "Afternoon", owned_tops, owned_bots, [], False, False)
print("SUCCESS:", ok)
if ok:
    print("AI TARGET:", out[0], out[1])
    print("BT1:", out[2])
    print("BB1:", out[3])
else:
    print("FAILED TO FIND OUTFIT")
