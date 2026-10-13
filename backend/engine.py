import os
import json
import random
import requests
import joblib
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional

OWM_API_KEY = "3795ac331def1d702f917c283a417051"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _resolve_path(filename, subfolder):
    p_sub = os.path.join(BASE_DIR, subfolder, filename)
    if os.path.exists(p_sub): return p_sub
    p_root = os.path.join(BASE_DIR, filename)
    if os.path.exists(p_root): return p_root
    return p_sub

DB_JSON_PATH = _resolve_path("wardrobe_db.json", "data")
MODEL_PATH = _resolve_path("wardrobe_model.pkl", "models")

# Translations for engine messages
TEXTS = {
    "en": {
        "warn_rain": "⚠️ Rain is expected later. We styled you for now, but don't forget to take your **{carry}**!",
        "warn_rain_fallback": "⚠️ Rain is expected later! No umbrella or hooded item found in your wardrobe, be careful!",
        "warn_snow": "❄️ Snow is expected later! Make sure to carry winter-ready outerwear.",
        "warn_temp": "📉 Temperature will drop to {t:.1f}°C later. We styled you for now, but recommend carrying: **{carry}**",
        "warn_temp_fallback": "📉 Temperature will drop to {t:.1f}°C later. Bring some outerwear!",
        "warn_warm": "☀️ Temperature will rise to {t:.1f}°C later. Outfit designed with removable layers (onion strategy) so you don't overheat!",
        "warn_no_shorts": "👖 Long pants selected instead of shorts to protect your legs from the cold/rain expected later!",
        "warn_fallback_outfit": "⚠️ No perfectly matching items found in your wardrobe for this weather. The closest alternatives were suggested.",
        "info_offset": "⏱️ Outfit generated for {h} hours from now ({t:.1f}°C base temp).",
        "warn_rain_temp_umbrella": "⚠️ Later today, temperature will drop to {t:.1f}°C and rain is expected! We styled you for now, but recommend taking your **{carry_rain}** and **{carry_temp}**!",
        "warn_rain_temp_combo": "⚠️ Later today, temperature will drop to {t:.1f}°C and rain is expected! To stay protected from both cold and rain with a single piece, carry your **{carry}**!",
        "warn_rain_temp_fallback": "⚠️ Later today, temperature will drop to {t:.1f}°C and rain is expected! You can take **{carry}** for the cold, but we strongly recommend carrying an umbrella as well."
    },
    "tr": {
        "warn_rain": "⚠️ İlerleyen saatlerde YAĞMUR bekleniyor. Kombininiz şu anki havaya göre yapıldı, yanınıza mutlaka **{carry}** alın!",
        "warn_rain_fallback": "⚠️ İlerleyen saatlerde YAĞMUR bekleniyor. Dolabınızda şemsiye veya kapüşonlu bulunamadı, dikkatli olun!",
        "warn_snow": "❄️ İlerleyen saatlerde KAR bekleniyor. Yanınıza kara hazırlıklı dış giyim almayı unutmayın!",
        "warn_temp": "📉 Hava ilerleyen saatlerde {t:.1f}°C'ye kadar soğuyacak. Kombininiz şimdiki havaya göre yapıldı, yanınıza ekstra olarak **{carry}** almanızı öneririz!",
        "warn_temp_fallback": "📉 Hava ilerleyen saatlerde {t:.1f}°C'ye kadar soğuyacak. Yanınıza mutlaka kalın bir dış giyim alın!",
        "warn_warm": "☀️ Hava ilerleyen saatlerde {t:.1f}°C'ye kadar ısınacak. Öğlen terlememeniz için kombin 'çıkarılabilir katmanlı (soğan taktiği)' olarak özel ayarlandı!",
        "warn_no_shorts": "👖 Şu an sıcak olsa da ilerleyen saatlerde havanın soğuyacağı/bozacağı öngörüldü. Bacaklarınızın üşümemesi için şort yerine uzun pantolon tercih edildi!",
        "warn_fallback_outfit": "⚠️ Dolabınızda bu havaya tam uygun yalıtımda kıyafet bulunamadığı için, mevcut olan en iyi alternatifler önerildi.",
        "info_offset": "⏱️ Kombin {h} saat sonraki hava durumu ({t:.1f}°C) baz alınarak oluşturuldu.",
        "warn_rain_temp_umbrella": "⚠️ İlerleyen saatlerde hava {t:.1f}°C'ye soğuyacak ve yağmur bekleniyor! Kombininiz şimdiki havaya göre yapıldı; yanınıza **{carry_rain}** ve **{carry_temp}** almanızı öneririz!",
        "warn_rain_temp_combo": "⚠️ İlerleyen saatlerde hava {t:.1f}°C'ye soğuyacak ve yağmur başlayacak! Hem soğuktan hem yağmurdan tek parça ile korunmak için yanınıza **{carry}** almanız yeterli olacaktır.",
        "warn_rain_temp_fallback": "⚠️ İlerleyen saatlerde hava {t:.1f}°C'ye soğuyacak ve yağmur bekleniyor. Soğuk için yanınıza **{carry}** alabilirsiniz; ancak dolabınızda yağmura uygun bir dış giyim bulunmadığı için yanınıza mutlaka bir şemsiye edinmenizi öneririz."
    }
}

# Load assets
_db_cache = None
_model_cache = None

def load_db() -> Dict:
    global _db_cache
    if _db_cache is None:
        with open(DB_JSON_PATH, "r", encoding="utf-8") as f:
            _db_cache = json.load(f)
    return _db_cache

def load_model():
    global _model_cache
    if _model_cache is None:
        if os.path.exists(MODEL_PATH):
            _model_cache = joblib.load(MODEL_PATH)
    return _model_cache

def get_current_weather(city: str) -> Tuple[bool, Any, Any, Any, Any, Any, Any]:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=metric"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("cod") == 200:
            temp = res["main"]["temp"]
            feels_like = res["main"]["feels_like"]
            condition = res["weather"][0]["main"]
            desc = res["weather"][0]["description"].capitalize()
            wind_kmh = round(res["wind"]["speed"] * 3.6, 1)
            icon = res["weather"][0]["icon"]
            return True, temp, feels_like, condition, desc, wind_kmh, icon
    except Exception:
        pass
    return False, 0, 0, "", "", 0, ""

def get_trip_forecast(city: str, start_offset_hours: int = 0, duration_hours: int = 4) -> Tuple[bool, List[float], List[str]]:
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OWM_API_KEY}&units=metric"
    try:
        res = requests.get(url, timeout=5).json()
        if res.get("cod") == "200":
            flcs = []
            precips = []
            start_slot = max(0, start_offset_hours // 3)
            slots_needed = max(1, (duration_hours + 2) // 3)
            
            items = res["list"][start_slot : start_slot + slots_needed + 1]
            for item in items:
                flcs.append(item["main"]["feels_like"])
                w_main = item["weather"][0]["main"]
                if "Rain" in w_main or "Drizzle" in w_main:
                    precips.append("Rain")
                elif "Snow" in w_main:
                    precips.append("Snow")
                else:
                    precips.append("Clear")
            return True, flcs, precips
    except Exception:
        pass
    return False, [], []

def fmt_item(item: Dict, lang: str = "tr") -> str:
    name = item.get(lang, item.get("en", ""))
    icon = item.get("icon", "")
    return f"{icon} {name}".strip()

def is_style_compatible(s1: List[str], s2: List[str]) -> bool:
    if "Universal" in s1 or "Universal" in s2:
        return True
    return bool(set(s1).intersection(set(s2)))

def generate_recommendations(
    user_gender: str,
    base_thermal_profile: str,
    personal_delta_clo: float,
    has_umbrella: bool,
    has_undershirt: bool,
    user_wardrobe_items: Dict[str, List[str]], # Category -> List[item_en]
    city: str,
    start_offset: int = 0,
    duration: int = 4,
    lang: str = "tr"
) -> Dict[str, Any]:
    """
    Main recommendation engine incorporating:
    - User's persistent wardrobe
    - Dynamic Personalization: personal_delta_clo
    - Time-travel trip forecasting
    - Onion strategy (warm later)
    - Ban shorts (cold/rain/wind)
    - Wind penalty
    - Unified smart warnings
    - 3 Diverse outfits
    """
    kiyafet_db = load_db()
    model = load_model()
    
    # 1. Fetch current & trip weather
    ok, temp_c, feels_like_c, cond, desc, wind_kmh, icon = get_current_weather(city)
    if not ok:
        # Fallback to standard mock weather if offline
        temp_c, feels_like_c, cond, desc, wind_kmh, icon = 20.0, 19.5, "Clouds", "Parçalı Bulutlu", 12.0, "03d"
        
    precip_ml = "Rain" if ("Rain" in cond or "Drizzle" in cond) else ("Snow" if "Snow" in cond else "Clear")
    
    # Estimate time of day
    from datetime import datetime
    current_hour = (datetime.now().hour + start_offset) % 24
    if 5 <= current_hour < 12:
        time_ml = "Morning"
    elif 12 <= current_hour < 18:
        time_ml = "Afternoon"
    else:
        time_ml = "Evening"
        
    warnings = []
    trip_flc = feels_like_c
    trip_precip = precip_ml
    
    layering_needed = False
    ban_shorts = False
    
    # 2. Trip Forecast & Warnings Analysis
    if start_offset > 0 or duration > 2:
        ok_f, f_flcs, f_pre = get_trip_forecast(city, start_offset, duration)
        if ok_f and f_flcs:
            if start_offset == 0:
                all_temps = [feels_like_c] + f_flcs
                all_precips = [precip_ml] + f_pre
            else:
                all_temps = f_flcs
                all_precips = f_pre
                
            base_flc = all_temps[0]
            base_precip = all_precips[0]
            trip_flc = base_flc
            trip_precip = base_precip
            
            min_flc = min(all_temps)
            max_flc = max(all_temps)
            
            if (max_flc - base_flc) >= 4:
                layering_needed = True
                warnings.append(TEXTS[lang]["warn_warm"].format(t=max_flc))
                
            is_snow = "Snow" in all_precips and base_precip != "Snow"
            is_rain = "Rain" in all_precips and base_precip != "Rain"
            is_temp_drop = (base_flc - min_flc) >= 3
            
            if (min_flc < 19) or ("Rain" in all_precips) or ("Snow" in all_precips):
                ban_shorts = True
                if base_flc >= 22:
                    warnings.append(TEXTS[lang]["warn_no_shorts"])
                    
            best_carry = None
            if is_temp_drop:
                extra_clo = (base_flc - min_flc) * 0.08
                best_diff = 999
                for item in kiyafet_db["top_outer"]:
                    if item["en"] in user_wardrobe_items.get("top_outer", []) and item["en"] != "None (Innerwear Only)":
                        diff = abs(item["clo"] - extra_clo)
                        if diff < best_diff:
                            best_diff = diff
                            best_carry = fmt_item(item, lang)
                            
            if is_snow:
                warnings.append(TEXTS[lang]["warn_snow"])
                
            # Unified Smart Alert
            if is_rain and is_temp_drop:
                if has_umbrella:
                    umb_str = "☂️ Şemsiye" if lang == "tr" else "☂️ Umbrella"
                    if best_carry:
                        warnings.append(TEXTS[lang]["warn_rain_temp_umbrella"].format(t=min_flc, carry_rain=umb_str, carry_temp=best_carry))
                    else:
                        warnings.append(TEXTS[lang]["warn_rain"].format(carry=umb_str))
                        warnings.append(TEXTS[lang]["warn_temp_fallback"].format(t=min_flc))
                else:
                    combo_carry = None
                    combo_diff = 999
                    for item in kiyafet_db["top_outer"]:
                        if item["en"] in user_wardrobe_items.get("top_outer", []) and item["en"] != "None (Innerwear Only)" and item.get("hoodie", False):
                            diff = abs(item["clo"] - extra_clo)
                            if diff < combo_diff:
                                combo_diff = diff
                                combo_carry = fmt_item(item, lang)
                    if combo_carry:
                        warnings.append(TEXTS[lang]["warn_rain_temp_combo"].format(t=min_flc, carry=combo_carry))
                    elif best_carry:
                        warnings.append(TEXTS[lang]["warn_rain_temp_fallback"].format(t=min_flc, carry=best_carry))
                    else:
                        warnings.append(TEXTS[lang]["warn_rain_fallback"])
                        warnings.append(TEXTS[lang]["warn_temp_fallback"].format(t=min_flc))
            elif is_rain:
                rain_item = None
                if not has_umbrella:
                    for item in kiyafet_db["top_outer"]:
                        if item["en"] in user_wardrobe_items.get("top_outer", []) and item.get("hoodie", False):
                            rain_item = fmt_item(item, lang)
                            break
                if has_umbrella:
                    umb_str = "☂️ Şemsiye" if lang == "tr" else "☂️ Umbrella"
                    warnings.append(TEXTS[lang]["warn_rain"].format(carry=umb_str))
                elif rain_item:
                    warnings.append(TEXTS[lang]["warn_rain"].format(carry=rain_item))
                else:
                    warnings.append(TEXTS[lang]["warn_rain_fallback"])
            elif is_temp_drop:
                if best_carry:
                    warnings.append(TEXTS[lang]["warn_temp"].format(t=min_flc, carry=best_carry))
                else:
                    warnings.append(TEXTS[lang]["warn_temp_fallback"].format(t=min_flc))

    # 3. Calculate Target CLO using ML + Personal Adaptive Bias
    target_top = 0.5
    target_bot = 0.3
    
    if model:
        try:
            profile_map = {"Cold": "Üşüyen", "Standard": "Standart", "Hot": "Sıcakkanlı"}
            p_val = profile_map.get(base_thermal_profile, "Standart")
            
            inp = pd.DataFrame([{
                'feels_like': trip_flc,
                'precipitation': trip_precip,
                'wind_speed_kmh': wind_kmh,
                'time_of_day': time_ml,
                'user_profile': p_val
            }])
            
            top_classes = model['top_model'].classes_
            bot_classes = model['bottom_model'].classes_
            
            # Predict
            top_preds = model['top_model'].predict_proba(inp)[0]
            bot_preds = model['bottom_model'].predict_proba(inp)[0]
            
            # Filter for 'Comfortable'
            valid_targets = []
            for i, tc in enumerate(top_classes):
                for j, bc in enumerate(bot_classes):
                    if "Comfortable" in tc and "Comfortable" in bc:
                        prob = top_preds[i] * bot_preds[j]
                        if prob > 0.005:
                            t_clo = float(tc.split("_")[0])
                            b_clo = float(bc.split("_")[0])
                            valid_targets.append((t_clo, b_clo, prob))
                            
            if valid_targets:
                valid_targets.sort(key=lambda x: x[2], reverse=True)
                target_top = valid_targets[0][0]
                target_bot = valid_targets[0][1]
        except Exception:
            pass

    # Apply Dynamic Personalization Bias (Online Learning Parameter)
    target_top = round(max(0.1, target_top + personal_delta_clo * 0.65), 2)
    target_bot = round(max(0.1, target_bot + personal_delta_clo * 0.35), 2)
    
    # Handle Undershirt deduction
    tt_search = target_top
    used_undershirt = False
    if has_undershirt and trip_flc < 18:
        atlet_item = next((x for x in kiyafet_db["top_inner"] if x["en"] == "Sleeveless T-Shirt"), None)
        if atlet_item:
            tt_search = max(0.1, tt_search - atlet_item["clo"])
            used_undershirt = True

    # 4. Search Wardrobe for Combos
    owned_top_in = user_wardrobe_items.get("top_inner", [])
    owned_top_out = user_wardrobe_items.get("top_outer", [])
    owned_bot_in = user_wardrobe_items.get("bottom_inner", [])
    owned_bot_out = user_wardrobe_items.get("bottom_outer", [])
    owned_acc = user_wardrobe_items.get("accessories", [])

    s_tops_temp = []
    for ic in kiyafet_db["top_inner"]:
        for dis in kiyafet_db["top_outer"]:
            if ic["en"] not in owned_top_in or dis["en"] not in owned_top_out:
                continue
            if user_gender not in ic["gender"] or user_gender not in dis["gender"]:
                continue
            if trip_precip in ["Rain", "Snow"] and dis["en"] == "None (Innerwear Only)":
                continue
            if layering_needed:
                if dis["en"] == "None (Innerwear Only)":
                    continue
                if ic["clo"] > 0.20:
                    continue
            if not is_style_compatible(ic["style"], dis["style"]):
                continue
                
            top_style = dis["style"] if "Universal" in ic["style"] else (ic["style"] if "Universal" in dis["style"] else list(set(ic["style"]).intersection(set(dis["style"]))))
            diff = abs((ic["clo"] + dis["clo"]) - tt_search)
            s_tops_temp.append({
                "ic": fmt_item(ic, lang),
                "dis": fmt_item(dis, lang),
                "ic_en": ic["en"],
                "dis_en": dis["en"],
                "basic": ic.get("basic", False) and dis.get("basic", False),
                "style": top_style,
                "clo": ic["clo"] + dis["clo"],
                "diff": diff
            })

    s_tops = [x for x in s_tops_temp if x["diff"] <= 0.25]
    if not s_tops and s_tops_temp:
        s_tops_temp.sort(key=lambda x: x["diff"])
        s_tops = [x for x in s_tops_temp if x["diff"] <= s_tops_temp[0]["diff"] + 0.05]

    s_bots_temp = []
    for ic in kiyafet_db["bottom_inner"]:
        for dis in kiyafet_db["bottom_outer"]:
            if ic["en"] not in owned_bot_in or dis["en"] not in owned_bot_out:
                continue
            if user_gender not in ic["gender"] or user_gender not in dis["gender"]:
                continue
            if trip_precip in ["Rain", "Snow"] and "Shorts" in dis["en"]:
                continue
            if trip_flc < 20 and "Shorts" in dis["en"]:
                continue
            if dis["en"] == "Shorts" and ic["en"] != "None (Underwear Only)":
                continue
            if ban_shorts and "Shorts" in dis["en"]:
                continue
            if trip_flc < 25 and wind_kmh > 20 and "Shorts" in dis["en"]:
                continue
            if not is_style_compatible(ic["style"], dis["style"]):
                continue
                
            bot_style = dis["style"] if "Universal" in ic["style"] else (ic["style"] if "Universal" in dis["style"] else list(set(ic["style"]).intersection(set(dis["style"]))))
            diff = abs((ic["clo"] + dis["clo"]) - target_bot)
            s_bots_temp.append({
                "ic": fmt_item(ic, lang),
                "dis": fmt_item(dis, lang),
                "ic_en": ic["en"],
                "dis_en": dis["en"],
                "basic": ic.get("basic", False) and dis.get("basic", False),
                "style": bot_style,
                "clo": ic["clo"] + dis["clo"],
                "diff": diff
            })

    s_bots = [x for x in s_bots_temp if x["diff"] <= 0.30]
    if not s_bots and s_bots_temp:
        s_bots_temp.sort(key=lambda x: x["diff"])
        s_bots = [x for x in s_bots_temp if x["diff"] <= s_bots_temp[0]["diff"] + 0.05]

    # Accessories
    accs = []
    if trip_precip == "Clear" and time_ml in ["Morning", "Afternoon"] and trip_flc > 15:
        if "Sunglasses" in owned_acc:
            accs.append("🕶️ Güneş Gözlüğü" if lang == "tr" else "🕶️ Sunglasses")
    if trip_flc < 10:
        if "Beanie (Hat)" in owned_acc:
            accs.append("🧶 Bere" if lang == "tr" else "🧶 Beanie")
        if "Scarf" in owned_acc:
            accs.append("🧣 Atkı" if lang == "tr" else "🧣 Scarf")
    if trip_flc < 5:
        if "Leather/Winter Gloves" in owned_acc:
            accs.append("🧤 Eldiven" if lang == "tr" else "🧤 Gloves")

    valid_outfits = []
    for top in s_tops:
        for bot in s_bots:
            if is_style_compatible(top["style"], bot["style"]):
                diff = abs(top["clo"] - tt_search) + abs(bot["clo"] - target_bot)
                valid_outfits.append((top, bot, diff))

    if not valid_outfits:
        return {
            "success": False,
            "message": "Dolabınızdaki parçalarla uygun kombin bulunamadı." if lang == "tr" else "No matching outfit found in wardrobe.",
            "weather": {"temp": temp_c, "feels_like": trip_flc, "condition": desc, "wind_kmh": wind_kmh}
        }

    valid_outfits.sort(key=lambda x: x[2])
    clean_outfits = [(x[0], x[1]) for x in valid_outfits]

    basics = [x for x in clean_outfits if x[0]["basic"] and x[1]["basic"]]
    bt1, bb1 = random.choice(basics[:3]) if basics else random.choice(clean_outfits[:3])

    def get_diverse(pool, avoid_tops, avoid_bots):
        p1 = [x for x in pool if x[0]["ic_en"] not in avoid_tops and x[1]["ic_en"] not in avoid_bots]
        if p1: return random.choice(p1[:4])
        p2 = [x for x in pool if x[1]["ic_en"] not in avoid_bots]
        if p2: return random.choice(p2[:3])
        p3 = [x for x in pool if x[0]["ic_en"] not in avoid_tops]
        if p3: return random.choice(p3[:3])
        return random.choice(pool[:3])

    bt2, bb2 = get_diverse(clean_outfits, [bt1["ic_en"]], [bb1["ic_en"]])
    
    non_basics = [x for x in clean_outfits if not (x[0]["basic"] and x[1]["basic"])]
    if non_basics:
        at, ab = get_diverse(non_basics, [bt1["ic_en"], bt2["ic_en"]], [bb1["ic_en"], bb2["ic_en"]])
    else:
        at, ab = get_diverse(clean_outfits, [bt1["ic_en"], bt2["ic_en"]], [bb1["ic_en"], bb2["ic_en"]])

    return {
        "success": True,
        "weather": {
            "temp": round(temp_c, 1),
            "feels_like": round(trip_flc, 1),
            "condition": desc,
            "wind_kmh": wind_kmh,
            "icon": icon,
            "time_of_day": time_ml
        },
        "target_clo": {
            "top": round(target_top, 2),
            "bottom": round(target_bot, 2),
            "personal_delta": personal_delta_clo
        },
        "warnings": warnings,
        "undershirt_used": used_undershirt,
        "outfits": {
            "daily": {
                "title": "Seçenek 1 (Günlük)" if lang == "tr" else "Option 1 (Daily)",
                "top": f"{bt1['ic']} + {bt1['dis']}" if bt1['dis_en'] != "None (Innerwear Only)" else bt1['ic'],
                "bottom": f"{bb1['ic']} + {bb1['dis']}" if bb1['ic_en'] != "None (Underwear Only)" else bb1['dis'],
                "clo": round(bt1['clo'] + bb1['clo'], 2)
            },
            "alternative": {
                "title": "Seçenek 2 (Alternatif)" if lang == "tr" else "Option 2 (Alternative)",
                "top": f"{bt2['ic']} + {bt2['dis']}" if bt2['dis_en'] != "None (Innerwear Only)" else bt2['ic'],
                "bottom": f"{bb2['ic']} + {bb2['dis']}" if bb2['ic_en'] != "None (Underwear Only)" else bb2['dis'],
                "clo": round(bt2['clo'] + bb2['clo'], 2)
            },
            "unique": {
                "title": "Seçenek 3 (Dikkat Çekici)" if lang == "tr" else "Option 3 (Unique)",
                "top": f"{at['ic']} + {at['dis']}" if at['dis_en'] != "None (Innerwear Only)" else at['ic'],
                "bottom": f"{ab['ic']} + {ab['dis']}" if ab['ic_en'] != "None (Underwear Only)" else ab['dis'],
                "clo": round(at['clo'] + ab['clo'], 2)
            }
        },
        "accessories": accs
    }
