import json

with open("wardrobe_db.json", "r", encoding="utf-8") as f:
    kiyafet_db = json.load(f)

def fmt(item, lang): return f"{item['icon']} {item[lang]}" if "icon" in item else item[lang]
def is_style_compatible(s1, s2):
    if "Universal" in s1 or "Universal" in s2: return True
    return len(set(s1).intersection(set(s2))) > 0

lang = 'tr'
ml_gender = 'Male'
feels_like_c = 23.2
wind_kmh = 27.8
tt = 0.1
tb = 0.1

owned_tops = [fmt(x, lang) for x in kiyafet_db["top_inner"] if x["en"] in ["Short Sleeve T-Shirt", "Shirt", "Thin Knit Sweater", "Hoodie"]]
owned_tops += [fmt(x, lang) for x in kiyafet_db["top_outer"] if x["en"] in ["Thin Windbreaker", "Cardigan", "Winter Puffer Jacket"]]
owned_tops.append(fmt(next(x for x in kiyafet_db["top_outer"] if x["en"] == "None (Innerwear Only)"), lang))

owned_bots = [fmt(x, lang) for x in kiyafet_db["bottom_outer"] if x["en"] in ["Jeans", "Sweatpants", "Shorts"]]
owned_bots.append(fmt(next(x for x in kiyafet_db["bottom_inner"] if x["en"] == "None (Underwear Only)"), lang))

s_tops, s_bots = [], []
for ic in kiyafet_db["top_inner"]:
    for dis in kiyafet_db["top_outer"]:
        ic_str, dis_str = fmt(ic, lang), fmt(dis, lang)
        if ic_str not in owned_tops or dis_str not in owned_tops: continue
        if ml_gender not in ic["gender"] or ml_gender not in dis["gender"]: continue
        
        is_no = dis["en"] == "None (Innerwear Only)"
        if feels_like_c < 19 and ic["en"] in ["Short Sleeve T-Shirt", "Sleeveless T-Shirt", "Tank Top / Crop Top", "Elegant Blouse", "Polo T-Shirt"] and is_no: continue
        if feels_like_c < 22 and wind_kmh > 15 and is_no: continue
        if not is_style_compatible(ic["style"], dis["style"]): continue
        if abs((ic["clo"] + dis["clo"]) - tt) <= 0.15:
            top_style = list(set(ic["style"]).intersection(set(dis["style"]))) if not ("Universal" in ic["style"] or "Universal" in dis["style"]) else (dis["style"] if "Universal" in ic["style"] else ic["style"])
            s_tops.append({"ic": ic_str, "dis": dis_str, "basic": ic["basic"] and dis["basic"], "style": top_style})

print("S_TOPS:", len(s_tops))
for t in s_tops: print(t["ic"], "+", t["dis"])

for ic in kiyafet_db["bottom_inner"]:
    for dis in kiyafet_db["bottom_outer"]:
        ic_str, dis_str = fmt(ic, lang), fmt(dis, lang)
        if ic_str not in owned_bots or dis_str not in owned_bots: continue
        if ml_gender not in ic["gender"] or ml_gender not in dis["gender"]: continue
        if dis["en"] == "Shorts" and ic["en"] != "None (Underwear Only)": continue
        if not is_style_compatible(ic["style"], dis["style"]): continue
        if abs((ic["clo"] + dis["clo"]) - tb) <= 0.15:
            bot_style = list(set(ic["style"]).intersection(set(dis["style"]))) if not ("Universal" in ic["style"] or "Universal" in dis["style"]) else (dis["style"] if "Universal" in ic["style"] else ic["style"])
            s_bots.append({"ic": ic_str, "dis": dis_str, "basic": ic["basic"] and dis["basic"], "style": bot_style})

print("S_BOTS:", len(s_bots))
for b in s_bots: print(b["ic"], "+", b["dis"])

valid_outfits = []
for top in s_tops:
    for bot in s_bots:
        if is_style_compatible(top["style"], bot["style"]):
            valid_outfits.append((top, bot))

print("VALID:", len(valid_outfits))

