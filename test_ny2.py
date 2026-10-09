import json, joblib

with open("wardrobe_db.json", "r", encoding="utf-8") as f:
    kiyafet_db = json.load(f)

def fmt(item, lang):
    return f"{item['icon']} {item[lang]}" if "icon" in item else item[lang]

def is_style_compatible(styles1, styles2):
    if "Universal" in styles1 or "Universal" in styles2: return True
    return len(set(styles1).intersection(set(styles2))) > 0

data = joblib.load("wardrobe_model.pkl")
model = data['model']
encoders = data['encoders']

def test_ny():
    lang = 'tr'
    feels_like_c = 23.2
    precip_ml = "Clear"
    wind_kmh = 27.8
    time_ml = "Afternoon"
    has_umbrella = False
    has_undershirt = False
    
    gen_enc = encoders['gender'].transform(["Male"])[0]
    prof_enc = encoders['profile'].transform(["Standard"])[0]
    precip_enc = encoders['precip'].transform([precip_ml])[0]
    time_enc = encoders['time'].transform([time_ml])[0]
    comf_enc = encoders['outcome'].transform(['Comfortable'])[0]
    
    valid = []
    for u in [x*0.1 for x in range(2,20)]:
        for a in [x*0.1 for x in range(1,10)]:
            if a > u + 0.1: continue
            if feels_like_c >= 20 and (u - a) > 0.3: continue
            if feels_like_c < 20 and u < 0.3: continue
            if feels_like_c < 20 and a < 0.2: continue
            if model.predict([[gen_enc, prof_enc, feels_like_c, precip_enc, wind_kmh, time_enc, u, a]])[0] == comf_enc:
                valid.append((u, a))
                
    if valid:
        tt = sum([h[0] for h in valid]) / len(valid)
        tb = sum([h[1] for h in valid]) / len(valid)
        print("ML FOUND TARGETS:", tt, tb)
    else:
        print("ML FAILED. USING FALLBACK.")
        base = max(0.2, (22 - feels_like_c) * 0.10)
        if time_ml == "Evening": base += 0.15
        elif time_ml == "Afternoon" and precip_ml == "Clear": base -= 0.10
        tt, tb = round(base*0.65, 1), round(base*0.35, 1)
        print("FALLBACK TARGETS:", tt, tb)

    # Let's see what it accepts for tops
    s_tops = []
    for ic in kiyafet_db["top_inner"]:
        for dis in kiyafet_db["top_outer"]:
            is_no = dis["en"] == "None (Innerwear Only)"
            if feels_like_c < 19 and ic["en"] in ["Short Sleeve T-Shirt", "Sleeveless T-Shirt", "Tank Top / Crop Top", "Elegant Blouse", "Polo T-Shirt"] and is_no: continue
            if feels_like_c < 22 and wind_kmh > 15 and is_no: continue
            if not is_style_compatible(ic["style"], dis["style"]): continue
            if abs((ic["clo"] + dis["clo"]) - tt) <= 0.15:
                s_tops.append((ic["en"], dis["en"], ic["clo"]+dis["clo"]))
    
    print("VALID TOPS:", len(s_tops))
    for t in s_tops: print("  ", t)

    s_bots = []
    for ic in kiyafet_db["bottom_inner"]:
        for dis in kiyafet_db["bottom_outer"]:
            if precip_ml in ["Rain", "Snow"] and "Shorts" in dis["en"]: continue
            if feels_like_c < 20 and "Shorts" in dis["en"]: continue
            if dis["en"] == "Shorts" and ic["en"] != "None (Underwear Only)": continue
            if not is_style_compatible(ic["style"], dis["style"]): continue
            if abs((ic["clo"] + dis["clo"]) - tb) <= 0.15:
                s_bots.append((ic["en"], dis["en"], ic["clo"]+dis["clo"]))
    print("VALID BOTS:", len(s_bots))
    for b in s_bots: print("  ", b)

test_ny()
