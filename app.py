import streamlit as st
import pandas as pd
import joblib
import random
import os
import requests
import datetime
import json

st.set_page_config(page_title="Smart Wardrobe Assistant", page_icon="🧥", layout="wide", initial_sidebar_state="expanded")

API_KEY = "3795ac331def1d702f917c283a417051"

t = {
    "en": {
        "welcome": "👋 Welcome to Smart Wardrobe Assistant!",
        "desc": "To recommend the best outfit for the weather, we need to know a little about you:",
        "q1": "1. What is your gender?",
        "q2": "2. What is your thermal profile?",
        "btn_save": "Save and Start 🚀",
        "female": "Female", "male": "Male",
        "cold": "Cold-natured", "std": "Standard", "hot": "Hot-blooded",
        "title": "🌦️ Smart AI Wardrobe Assistant",
        "err_model": "Model not found! Please run the training script first.",
        "prof_title": "👤 Your Profile",
        "gender_lbl": "Gender", "prof_lbl": "Thermal",
        "btn_edit": "Edit Profile",
        "umbrella": "I have an umbrella ☂️",
        "undershirt_lbl": "I wear an undershirt 🎽",
        "wardrobe_title": "🚪 My Wardrobe",
        "wardrobe_desc": "*Select the items you own:*",
        "wt1": "👕 Inner Tops", "wt2": "🧥 Outerwear", "wt3": "👖 Bottoms", "wt4": "🧦 Hosiery / Thermals", "wt5": "🧣 Accessories",
        "what_do_u_have": "What do you have?",
        "city_lbl": "🌍 Select City:",
        "city_other": "Other (Custom)",
        "city_type": "Type your city:",
        "live_success": "✅ Live Weather Fetched!",
        "temp": "Temperature", "cond": "Conditions / Time", "precip": "Precipitation", "wind": "Wind Speed",
        "wait_conn": "Waiting for connection...",
        "manual_mode": "🛠️ Presentation Mode: Manual Weather",
        "manual_active": "Manual test mode active.",
        "btn_suggest": "👗 Suggest an Outfit 👔",
        "ai_calc": "AI is calculating ideal insulation targets...",
        "ai_target": "🧠 **AI Target:** Top: **{u:.1f} CLO**, Bottom: **{a:.1f} CLO**",
        "success_outfit": "✅ **Custom Outfit Recommendations:**",
        "opt1": "### 👕 Option 1 (Daily)", "opt2": "### 👕 Option 2 (Alt)", "opt3": "### ✨ Option 3 (Unique)",
        "top": "**Top:**", "bottom": "**Bottom:**", "extra": "**➕ Extras:**",
        "err_outfit": "⚠️ Couldn't find a perfect match in your wardrobe for these specific conditions!",
        "none_top": "None (Innerwear Only)", "none_bottom": "None (Underwear Only)",
        "rain": "Rain", "snow": "Snow", "clear": "Clear",
        "tab1": "⏳ Right Now", "tab2": "📅 5-Day Planner",
        "plan_time_lbl": "Select time for daily forecast:",
        "btn_plan": "Generate 5-Day Plan 🗓️",
        "atlet_str": "Undershirt",
        "dur_lbl": "How many hours will you be outside?",
        "warn_rain": "⚠️ Rain is expected later. We styled you for now, but don't forget to take your **{carry}**!",
        "warn_rain_fallback": "⚠️ Rain is expected later! No umbrella or hooded item found in your wardrobe, be careful!",
        "warn_snow": "❄️ Snow is expected later! Make sure to carry winter-ready outerwear.",
        "warn_temp": "📉 Temperature will drop to {t:.1f}°C later. We styled you for now, but recommend carrying: **{carry}**",
        "warn_temp_fallback": "📉 Temperature will drop to {t:.1f}°C later. Bring some outerwear!",
        "warn_warm": "☀️ Temperature will rise to {t:.1f}°C later. Outfit designed with removable layers (onion strategy) so you don't overheat!",
        "warn_no_shorts": "👖 Long pants selected instead of shorts to protect your legs from the cold/rain expected later!",
        "warn_fallback_outfit": "⚠️ No perfectly matching items found in your wardrobe for this weather. The closest alternatives were suggested."
    },
    "tr": {
        "welcome": "👋 Akıllı Kıyafet Asistanına Hoş Geldiniz!",
        "desc": "Hava durumuna göre en doğru kombini önerebilmemiz için seni biraz tanımamız gerekiyor:",
        "q1": "1. Cinsiyetiniz nedir?",
        "q2": "2. Vücut Isı Profiliniz (Klimada nasılsınız?)",
        "btn_save": "Kaydet ve Başla 🚀",
        "female": "Kadın", "male": "Erkek",
        "cold": "Üşüyen", "std": "Standart", "hot": "Sıcakkanlı",
        "title": "🌦️ Akıllı Yapay Zeka Kıyafet Asistanı",
        "err_model": "Model bulunamadı! Lütfen önce eğitim betiğini çalıştırın.",
        "prof_title": "👤 Profiliniz",
        "gender_lbl": "Cinsiyet", "prof_lbl": "Isı Profili",
        "btn_edit": "Profili Düzenle",
        "umbrella": "Yanımda Şemsiyem Var ☂️",
        "undershirt_lbl": "İçlik / Atlet Giyerim 🎽",
        "wardrobe_title": "🚪 Dolabımı Düzenle",
        "wardrobe_desc": "*Sahip olduğunuz kıyafetleri ekleyin:*",
        "wt1": "👕 Üst İç Giyim", "wt2": "🧥 Dış Giyim", "wt3": "👖 Alt Giyim", "wt4": "🧦 İçlik ve Çorap", "wt5": "🧣 Aksesuarlar",
        "what_do_u_have": "Nelerin Var?",
        "city_lbl": "🌍 Şehir Seçin:",
        "city_other": "Diğer (Kendim Yazacağım)",
        "city_type": "Şehrinizi yazın:",
        "live_success": "✅ Canlı Hava Durumu Çekildi!",
        "temp": "Sıcaklık", "cond": "Durum / Zaman", "precip": "Yağış", "wind": "Rüzgar Hızı",
        "wait_conn": "Bağlantı bekleniyor...",
        "manual_mode": "🛠️ Sunum Modu: Manuel Hava Durumu",
        "manual_active": "Manuel test modu aktif.",
        "btn_suggest": "👗 Bana Kombin Öner 👔",
        "ai_calc": "Yapay zeka hesaplıyor...",
        "ai_target": "🧠 **Hedef:** Üst: **{u:.1f} CLO**, Alt: **{a:.1f} CLO**",
        "success_outfit": "✅ **Kombin Önerileri:**",
        "opt1": "### 👕 Seçenek 1 (Günlük)", "opt2": "### 👕 Seçenek 2 (Alternatif)", "opt3": "### ✨ Seçenek 3 (Farklı)",
        "top": "**Üst:**", "bottom": "**Alt:**", "extra": "**➕ Ekstra:**",
        "err_outfit": "⚠️ Dolabındaki kıyafetlerle tam uygun kombin bulunamadı!",
        "none_top": "Yok (Sadece İç Giyim)", "none_bottom": "Yok (Sadece İç Çamaşırı)",
        "rain": "Yağmur", "snow": "Kar", "clear": "Yok",
        "tab1": "⏳ Şu An", "tab2": "📅 5 Günlük Planlayıcı",
        "plan_time_lbl": "Tahminlerin Hangi Saat İçin Yapılmasını İstersin?",
        "btn_plan": "5 Günlük Plan Oluştur 🗓️",
        "atlet_str": "İçlik Atlet",
        "dur_lbl": "Dışarıda Kalma Süreniz (Saat):",
        "warn_rain": "⚠️ İlerleyen saatlerde YAĞMUR bekleniyor. Kombininiz şu anki havaya göre yapıldı, yanınıza mutlaka **{carry}** alın!",
        "warn_rain_fallback": "⚠️ İlerleyen saatlerde YAĞMUR bekleniyor. Dolabınızda şemsiye veya kapüşonlu bulunamadı, dikkatli olun!",
        "warn_snow": "❄️ İlerleyen saatlerde KAR bekleniyor. Yanınıza kara hazırlıklı dış giyim almayı unutmayın!",
        "warn_temp": "📉 Hava ilerleyen saatlerde {t:.1f}°C'ye kadar soğuyacak. Kombininiz şimdiki havaya göre yapıldı, yanınıza ekstra olarak **{carry}** almanızı öneririz!",
        "warn_temp_fallback": "📉 Hava ilerleyen saatlerde {t:.1f}°C'ye kadar soğuyacak. Yanınıza mutlaka kalın bir dış giyim alın!",
        "warn_warm": "☀️ Hava ilerleyen saatlerde {t:.1f}°C'ye kadar ısınacak. Öğlen terlememeniz için kombin 'çıkarılabilir katmanlı (soğan taktiği)' olarak özel ayarlandı!",
        "warn_no_shorts": "👖 Şu an sıcak olsa da ilerleyen saatlerde havanın soğuyacağı/bozacağı öngörüldü. Bacaklarınızın üşümemesi için şort yerine uzun pantolon tercih edildi!",
        "warn_fallback_outfit": "⚠️ Dolabınızda bu havaya tam uygun yalıtımda kıyafet bulunamadığı için, mevcut olan en iyi alternatifler önerildi."
    }
}

@st.cache_data
def load_db():
    with open(os.path.join(os.path.dirname(__file__), "wardrobe_db.json"), "r", encoding="utf-8") as f:
        return json.load(f)

kiyafet_db = load_db()

def fmt(item, lang):
    return f"{item['icon']} {item[lang]}" if "icon" in item else item[lang]

def is_style_compatible(styles1, styles2):
    if "Universal" in styles1 or "Universal" in styles2: return True
    return len(set(styles1).intersection(set(styles2))) > 0

if 'lang' not in st.session_state: st.session_state['lang'] = "en"
if 'onboarding_complete' not in st.session_state: st.session_state['onboarding_complete'] = False
if 'ml_gender' not in st.session_state: st.session_state['ml_gender'] = "Female"
if 'ml_profile' not in st.session_state: st.session_state['ml_profile'] = "Standard"

if not st.session_state['onboarding_complete']:
    lang_choice = st.radio("🌐 Language / Dil:", ["English", "Türkçe"], index=0 if st.session_state['lang']=="en" else 1, horizontal=True)
    st.session_state['lang'] = "en" if lang_choice == "English" else "tr"
    lang = st.session_state['lang']
    st.title(t[lang]["welcome"])
    st.markdown(t[lang]["desc"])
    st.markdown("---")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("onboarding_form"):
            cins_ui = st.radio(t[lang]["gender_lbl"], [t[lang]["female"], t[lang]["male"]])
            prof_ui = st.selectbox(t[lang]["prof_lbl"], [t[lang]["cold"], t[lang]["std"], t[lang]["hot"]])
            if st.form_submit_button(t[lang]["btn_save"], use_container_width=True):
                st.session_state['ml_gender'] = "Female" if cins_ui == t[lang]["female"] else "Male"
                if prof_ui == t[lang]["cold"]: st.session_state['ml_profile'] = "Cold-natured"
                elif prof_ui == t[lang]["hot"]: st.session_state['ml_profile'] = "Hot-blooded"
                else: st.session_state['ml_profile'] = "Standard"
                st.session_state['onboarding_complete'] = True
                st.rerun()
    st.stop()
else:
    lang = st.session_state['lang']

@st.cache_resource
def load_model_v2():
    file_path = os.path.join(os.path.dirname(__file__), "wardrobe_model.pkl")
    if not os.path.exists(file_path): return None, None
    data = joblib.load(file_path)
    return data['model'], data['encoders']

model, encoders = load_model_v2()

def get_live_weather(city, lang):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang={lang}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            weather_main = data["weather"][0]["main"]
            precip_ml = "Rain" if weather_main in ["Rain", "Drizzle", "Thunderstorm"] else ("Snow" if weather_main == "Snow" else "Clear")
            tz = data.get("timezone", 0)
            city_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=tz)
            return True, (data["main"]["temp"], data["main"]["feels_like"], precip_ml, data["wind"]["speed"]*3.6, data["weather"][0]["description"].title(), city_time.hour, city_time.strftime("%H:%M"))
        return False, f"API Error"
    except Exception as e: return False, str(e)

def get_5_day_forecast(city, target_time_str, lang):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang={lang}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            tz = data["city"]["timezone"]
            target_hour = 9 if target_time_str == "Morning" else (15 if target_time_str == "Afternoon" else 21)
            
            by_date = {}
            for item in data["list"]:
                dt = datetime.datetime.utcfromtimestamp(item["dt"]) + datetime.timedelta(seconds=tz)
                d_str = dt.strftime("%d %b")
                if d_str not in by_date: by_date[d_str] = []
                by_date[d_str].append((dt, item))
                
            results = []
            for d_str, items in by_date.items():
                if len(results) >= 5: break
                best = min(items, key=lambda x: abs(x[0].hour - target_hour))
                dt, item = best
                wm = item["weather"][0]["main"]
                p_ml = "Rain" if wm in ["Rain", "Drizzle", "Thunderstorm"] else ("Snow" if wm == "Snow" else "Clear")
                results.append({
                    "date": d_str, "time": dt.strftime("%H:%M"), "temp": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"], "precip": p_ml, "wind": item["wind"]["speed"]*3.6,
                    "desc": item["weather"][0]["description"].title()
                })
            return True, results
        return False, "API Error"
    except Exception as e: return False, str(e)

def get_trip_forecast(city, duration_hours):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            tz = data["city"]["timezone"]
            now = datetime.datetime.utcnow() + datetime.timedelta(seconds=tz)
            end_time = now + datetime.timedelta(hours=duration_hours)
            
            flcs = []
            precips = []
            
            for item in data["list"]:
                dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=tz) + datetime.timedelta(seconds=(item["dt"] - datetime.datetime.utcnow().timestamp()))
                # Daha güvenli dt hesaplama:
                dt = datetime.datetime.utcfromtimestamp(item["dt"]) + datetime.timedelta(seconds=tz)
                if dt > end_time + datetime.timedelta(hours=3): break
                if dt >= now - datetime.timedelta(hours=3):
                    flcs.append(item["main"]["feels_like"])
                    wm = item["weather"][0]["main"]
                    p_ml = "Rain" if wm in ["Rain", "Drizzle", "Thunderstorm"] else ("Snow" if wm == "Snow" else "Clear")
                    precips.append(p_ml)
            
            return True, flcs, precips
        return False, [], []
    except Exception as e:
        return False, [], []

def generate_outfit(feels_like_c, precip_ml, wind_kmh, time_ml, owned_tops, owned_bottoms, owned_accs, has_umbrella, has_undershirt, layering_needed=False, ban_shorts=False):
    gen_enc = encoders['gender'].transform([st.session_state['ml_gender']])[0]
    prof_enc = encoders['profile'].transform([st.session_state['ml_profile']])[0]
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
    else:
        base = max(0.2, (22 - feels_like_c) * 0.10)
        if time_ml == "Evening": base += 0.15
        elif time_ml == "Afternoon" and precip_ml == "Clear": base -= 0.10
        tt, tb = round(base*0.65, 1), round(base*0.35, 1)
        
    used_undershirt = False
    if has_undershirt and tt >= 0.25:
        tt_search = tt - 0.10
        used_undershirt = True
    else:
        tt_search = tt

    s_tops_temp, s_bots_temp = [], []
    for ic in kiyafet_db["top_inner"]:
        for dis in kiyafet_db["top_outer"]:
            ic_str, dis_str = fmt(ic, lang), fmt(dis, lang)
            if ic_str not in owned_tops or dis_str not in owned_tops: continue
            if st.session_state['ml_gender'] not in ic["gender"] or st.session_state['ml_gender'] not in dis["gender"]: continue
            if precip_ml in ["Rain", "Snow"] and not has_umbrella and not (ic["hoodie"] or dis["hoodie"]): continue 
            
            is_no = dis["en"] == "None (Innerwear Only)"
            if feels_like_c < 19 and ic["en"] in ["Short Sleeve T-Shirt", "Sleeveless T-Shirt", "Tank Top / Crop Top", "Elegant Blouse", "Polo T-Shirt"] and is_no: continue
            if feels_like_c < 22 and wind_kmh > 15 and is_no: continue
            
            if layering_needed:
                if is_no: continue
                if ic["clo"] > 0.20: continue
            
            if not is_style_compatible(ic["style"], dis["style"]): continue
            
            if "Universal" in ic["style"]: top_style = dis["style"]
            elif "Universal" in dis["style"]: top_style = ic["style"]
            else: top_style = list(set(ic["style"]).intersection(set(dis["style"])))
            
            diff = abs((ic["clo"] + dis["clo"]) - tt_search)
            s_tops_temp.append({"ic": ic_str, "dis": dis_str, "basic": ic["basic"] and dis["basic"], "style": top_style, "clo": ic["clo"] + dis["clo"], "diff": diff})

    if s_tops_temp:
        s_tops = [x for x in s_tops_temp if x["diff"] <= 0.25]
        if not s_tops:
            s_tops_temp.sort(key=lambda x: x["diff"])
            s_tops = [x for x in s_tops_temp if x["diff"] <= s_tops_temp[0]["diff"] + 0.05]
    else: s_tops = []
            
    for ic in kiyafet_db["bottom_inner"]:
        for dis in kiyafet_db["bottom_outer"]:
            ic_str, dis_str = fmt(ic, lang), fmt(dis, lang)
            if ic_str not in owned_bottoms or dis_str not in owned_bottoms: continue
            if st.session_state['ml_gender'] not in ic["gender"] or st.session_state['ml_gender'] not in dis["gender"]: continue
            if precip_ml in ["Rain", "Snow"] and "Shorts" in dis["en"]: continue
            if feels_like_c < 20 and "Shorts" in dis["en"]: continue
            if dis["en"] == "Shorts" and ic["en"] != "None (Underwear Only)": continue
            if ban_shorts and "Shorts" in dis["en"]: continue
            
            if not is_style_compatible(ic["style"], dis["style"]): continue
            
            if "Universal" in ic["style"]: bot_style = dis["style"]
            elif "Universal" in dis["style"]: bot_style = ic["style"]
            else: bot_style = list(set(ic["style"]).intersection(set(dis["style"])))
            
            diff = abs((ic["clo"] + dis["clo"]) - tb)
            s_bots_temp.append({"ic": ic_str, "dis": dis_str, "basic": ic["basic"] and dis["basic"], "style": bot_style, "clo": ic["clo"] + dis["clo"], "diff": diff})

    if s_bots_temp:
        s_bots = [x for x in s_bots_temp if x["diff"] <= 0.30]
        if not s_bots:
            s_bots_temp.sort(key=lambda x: x["diff"])
            s_bots = [x for x in s_bots_temp if x["diff"] <= s_bots_temp[0]["diff"] + 0.05]
    else: s_bots = []
                
    def get_acc(en_name):
        return next(fmt(x, lang) for x in kiyafet_db["accessories"] if x["en"] == en_name)
    
    used_fallback = False
    if s_tops and s_tops[0]["diff"] > 0.25: used_fallback = True
    if s_bots and s_bots[0]["diff"] > 0.30: used_fallback = True

                
    accs = []
    if precip_ml == "Clear" and time_ml in ["Morning", "Afternoon"] and feels_like_c > 15:
        sun_lbl = get_acc("Sunglasses")
        if sun_lbl in owned_accs: accs.append(sun_lbl)
    if feels_like_c < 10:
        hat_lbl = get_acc("Beanie (Hat)")
        scarf_lbl = get_acc("Scarf")
        if hat_lbl in owned_accs: accs.append(hat_lbl)
        if scarf_lbl in owned_accs: accs.append(scarf_lbl)
    if feels_like_c < 5:
        glove_lbl = get_acc("Leather/Winter Gloves")
        if glove_lbl in owned_accs: accs.append(glove_lbl)

    valid_outfits = []
    for top in s_tops:
        for bot in s_bots:
            if is_style_compatible(top["style"], bot["style"]):
                # Kombinin hedefe olan uzaklığını hesapla (Daha küçük = Daha iyi uyum)
                diff = abs(top["clo"] - tt_search) + abs(bot["clo"] - tb)
                valid_outfits.append((top, bot, diff))

    if valid_outfits:
        # En mükemmel ısı uyumuna göre sırala
        valid_outfits.sort(key=lambda x: x[2])
        valid_outfits = [(x[0], x[1]) for x in valid_outfits]
        
        basics = [x for x in valid_outfits if x[0]["basic"] and x[1]["basic"]]
        non_basics = [x for x in valid_outfits if not (x[0]["basic"] and x[1]["basic"])]
        
        # Seçenek 1: Hedef ısıya EN YAKIN ilk 3 temel kombinden birini seç
        if basics:
            bt1, bb1 = random.choice(basics[:3])
        else:
            bt1, bb1 = random.choice(valid_outfits[:3])
            
        def get_diverse(pool, avoid_tops, avoid_bots):
            # 1. Hem üst hem alt farklı olsun
            p1 = [x for x in pool if x[0]["ic"] not in avoid_tops and x[1]["ic"] not in avoid_bots]
            if p1: return random.choice(p1[:4])
            # 2. Sadece alt farklı olsun (Bacaklar farklı görünsün)
            p2 = [x for x in pool if x[1]["ic"] not in avoid_bots]
            if p2: return random.choice(p2[:3])
            # 3. Sadece üst farklı olsun
            p3 = [x for x in pool if x[0]["ic"] not in avoid_tops]
            if p3: return random.choice(p3[:3])
            # 4. Hiçbiri yoksa rastgele
            return random.choice(pool[:3]) if pool else None
            
        # Seçenek 2: Çeşitlilik Filtresi ile Temel Parça
        remaining_basics = [x for x in basics if x != (bt1, bb1)]
        res2 = get_diverse(remaining_basics, [bt1["ic"]], [bb1["ic"]])
        if res2:
            bt2, bb2 = res2
        else:
            remaining_all = [x for x in valid_outfits if x != (bt1, bb1)]
            res2_all = get_diverse(remaining_all, [bt1["ic"]], [bb1["ic"]])
            bt2, bb2 = res2_all if res2_all else (bt1, bb1)
            
        # Seçenek 3: Çeşitlilik Filtresi ile İddialı (Non-Basic) Parça
        remaining_for_unique = [x for x in valid_outfits if x not in [(bt1, bb1), (bt2, bb2)]]
        non_basics_rem = [x for x in remaining_for_unique if x in non_basics]
        
        res3 = get_diverse(non_basics_rem, [bt1["ic"], bt2["ic"]], [bb1["ic"], bb2["ic"]])
        if res3:
            at, ab = res3
        else:
            res3_all = get_diverse(remaining_for_unique, [bt1["ic"], bt2["ic"]], [bb1["ic"], bb2["ic"]])
            at, ab = res3_all if res3_all else (bt1, bb1)
            
        return True, (tt, tb, bt1, bb1, bt2, bb2, at, ab, accs, used_undershirt, used_fallback)
    
    if s_tops and s_bots:
        bt1 = next((x for x in s_tops if x["basic"]), s_tops[0])
        bb1 = next((x for x in s_bots if x["basic"]), s_bots[0])
        bt2 = random.choice([x for x in s_tops if x != bt1] or [bt1])
        bb2 = random.choice([x for x in s_bots if x != bb1] or [bb1])
        at = random.choice([x for x in s_tops if not x["basic"]] or [bt1])
        ab = random.choice([x for x in s_bots if not x["basic"]] or [bb1])
        return True, (tt, tb, bt1, bb1, bt2, bb2, at, ab, accs, used_undershirt, used_fallback)
        
    return False, None

st.title(t[lang]["title"])
if model is None: st.error(t[lang]["err_model"]); st.stop()

st.sidebar.header(t[lang]["prof_title"])
ui_gen = t[lang]["female"] if st.session_state['ml_gender'] == "Female" else t[lang]["male"]
ui_prof = t[lang]["cold"] if st.session_state['ml_profile'] == "Cold-natured" else (t[lang]["hot"] if st.session_state['ml_profile'] == "Hot-blooded" else t[lang]["std"])
st.sidebar.success(f"**{t[lang]['gender_lbl']}:** {ui_gen}  \n**{t[lang]['prof_lbl']}:** {ui_prof}")
if st.sidebar.button(t[lang]["btn_edit"]): st.session_state['onboarding_complete'] = False; st.rerun()

st.sidebar.markdown("---")
has_umbrella = st.sidebar.checkbox(t[lang]["umbrella"])
has_undershirt = st.sidebar.checkbox(t[lang]["undershirt_lbl"])

st.sidebar.header(t[lang]["wardrobe_title"])
top_inners = [fmt(x, lang) for x in kiyafet_db["top_inner"]]
top_outers = [fmt(x, lang) for x in kiyafet_db["top_outer"] if x["en"] != "None (Innerwear Only)"]
bottom_outers = [fmt(x, lang) for x in kiyafet_db["bottom_outer"]]
bottom_inners = [fmt(x, lang) for x in kiyafet_db["bottom_inner"] if x["en"] != "None (Underwear Only)"]
acc_items = [fmt(x, lang) for x in kiyafet_db["accessories"]]

def_ti = [fmt(x, lang) for x in kiyafet_db["top_inner"] if x["en"] in ["Short Sleeve T-Shirt", "Shirt", "Thin Knit Sweater", "Hoodie"]]
def_to = [fmt(x, lang) for x in kiyafet_db["top_outer"] if x["en"] in ["Thin Windbreaker", "Cardigan", "Winter Puffer Jacket"]]
def_bo = [fmt(x, lang) for x in kiyafet_db["bottom_outer"] if x["en"] in (["Jeans", "Sweatpants", "Tights (Sport/Thin)", "Shorts"] if st.session_state['ml_gender'] == "Female" else ["Jeans", "Sweatpants", "Shorts"])]
def_ac = [fmt(x, lang) for x in kiyafet_db["accessories"] if x["en"] in ["Beanie (Hat)", "Scarf", "Leather/Winter Gloves", "Sunglasses"]]

s_ti, s_to, s_bo, s_bi, s_ac = [], [], [], [], []
with st.sidebar.expander(t[lang]["wt1"]):
    for i, x in enumerate(top_inners):
        if st.checkbox(x, value=(x in def_ti), key=f"ti_{i}"): s_ti.append(x)
with st.sidebar.expander(t[lang]["wt2"]):
    for i, x in enumerate(top_outers):
        if st.checkbox(x, value=(x in def_to), key=f"to_{i}"): s_to.append(x)
with st.sidebar.expander(t[lang]["wt3"]):
    for i, x in enumerate(bottom_outers):
        if st.checkbox(x, value=(x in def_bo), key=f"bo_{i}"): s_bo.append(x)
with st.sidebar.expander(t[lang]["wt4"]):
    for i, x in enumerate(bottom_inners):
        if st.checkbox(x, value=False, key=f"bi_{i}"): s_bi.append(x)
with st.sidebar.expander(t[lang]["wt5"]):
    for i, x in enumerate(acc_items):
        if st.checkbox(x, value=(x in def_ac), key=f"ac_{i}"): s_ac.append(x)

none_t = fmt(next(x for x in kiyafet_db["top_outer"] if x["en"] == "None (Innerwear Only)"), lang)
none_b = fmt(next(x for x in kiyafet_db["bottom_inner"] if x["en"] == "None (Underwear Only)"), lang)

owned_tops = s_ti + s_to + [none_t]
owned_bots = s_bo + s_bi + [none_b]
owned_accs = s_ac

cities = ["Istanbul", "Ankara", "Izmir", "London", "New York", "Paris", "Tokyo", "Berlin", t[lang]["city_other"]]
sel_city = st.selectbox(t[lang]["city_lbl"], cities)
city = st.text_input(t[lang]["city_type"], "Seattle") if sel_city == t[lang]["city_other"] else sel_city

tab1, tab2 = st.tabs([t[lang]["tab1"], t[lang]["tab2"]])

def render_top(ic, dis, used_under):
    base_str = f"🎽 {t[lang]['atlet_str']} + " if used_under else ""
    if dis == none_t: return f"{base_str}{ic}"
    return f"{base_str}{ic} + {dis}"

def render_bot(ic, dis):
    if ic == none_b: return dis
    return f"{ic} + {dis}"

with tab1:
    if city:
        succ, res = get_live_weather(city, lang)
        if succ:
            tc, flc, p_ml, w_kmh, desc, chour, cstr = res
            tml = "Morning" if 5<=chour<12 else ("Afternoon" if 12<=chour<18 else "Evening")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(t[lang]["temp"], f"{tc:.1f}°C", f"Feels: {flc:.1f}°C" if lang=="en" else f"Hissedilen: {flc:.1f}°C", delta_color="off")
            t_ui = tml if lang=="en" else ("Sabah" if tml=="Morning" else ("Öğlen" if tml=="Afternoon" else "Akşam"))
            m2.metric(t[lang]["cond"], f"{desc}", f"{cstr} - {t_ui}", delta_color="off")
            p_ui = t[lang]["rain"] if p_ml=="Rain" else (t[lang]["snow"] if p_ml=="Snow" else t[lang]["clear"])
            m3.metric(t[lang]["precip"], p_ui)
            m4.metric(t[lang]["wind"], f"{w_kmh:.1f} km/h")
            
            st.markdown("---")
            duration = st.slider(t[lang]["dur_lbl"], min_value=1, max_value=12, value=1, step=1)
            
            if st.button(t[lang]["btn_suggest"], type="primary", key="btn_now"):
                with st.spinner(t[lang]["ai_calc"]):
                    trip_flc = flc
                    trip_precip = p_ml
                    warnings = []
                    
                    if duration > 2:
                        ok_f, f_flcs, f_pre = get_trip_forecast(city, duration)
                        if ok_f and f_flcs:
                            all_temps = [flc] + f_flcs
                            all_precips = [p_ml] + f_pre
                            
                            avg_flc = sum(all_temps) / len(all_temps)
                            min_flc = min(all_temps)
                            
                            max_flc = max(all_temps)
                            layering_needed = False
                            ban_shorts = False
                            
                            if (max_flc - flc) >= 4:
                                layering_needed = True
                                warnings.append(t[lang]["warn_warm"].format(t=max_flc))
                                
                            if "Snow" in all_precips and p_ml != "Snow":
                                warnings.append(t[lang]["warn_snow"])
                            elif "Rain" in all_precips and p_ml != "Rain":
                                rain_item = None
                                if not has_umbrella:
                                    for item in kiyafet_db["top_outer"]:
                                        if fmt(item, lang) in owned_tops and item["hoodie"]:
                                            rain_item = fmt(item, lang)
                                            break
                                if has_umbrella:
                                    umb_str = "☂️ Şemsiye" if lang == "tr" else "☂️ Umbrella"
                                    warnings.append(t[lang]["warn_rain"].format(carry=umb_str))
                                elif rain_item:
                                    warnings.append(t[lang]["warn_rain"].format(carry=rain_item))
                                else:
                                    warnings.append(t[lang]["warn_rain_fallback"])
                                    
                            if (min_flc < 19) or ("Rain" in all_precips) or ("Snow" in all_precips):
                                ban_shorts = True
                                if flc >= 22:
                                    warnings.append(t[lang]["warn_no_shorts"])
                                    
                            if (flc - min_flc) >= 3:
                                extra_clo = (flc - min_flc) * 0.08
                                best_carry = None
                                best_diff = 999
                                for item in kiyafet_db["top_outer"]:
                                    if fmt(item, lang) in owned_tops and item["en"] != "None (Innerwear Only)":
                                        diff = abs(item["clo"] - extra_clo)
                                        if diff < best_diff:
                                            best_diff = diff
                                            best_carry = fmt(item, lang)
                                            
                                if best_carry:
                                    warnings.append(t[lang]["warn_temp"].format(t=min_flc, carry=best_carry))
                                else:
                                    warnings.append(t[lang]["warn_temp_fallback"].format(t=min_flc))
                                # trip_flc bilerek değiştirilmiyor, böylece kombin ŞU AN'a göre yapılıyor
                                
                    for w in warnings:
                        st.warning(w)
                        
                    ok, out = generate_outfit(trip_flc, trip_precip, w_kmh, tml, owned_tops, owned_bots, owned_accs, has_umbrella, has_undershirt, layering_needed=layering_needed if 'layering_needed' in locals() else False, ban_shorts=ban_shorts if 'ban_shorts' in locals() else False)
                    if ok:
                        tt, tb, bt1, bb1, bt2, bb2, at, ab, accs, used_under, used_fallback = out
                        if used_fallback:
                            st.warning(t[lang]["warn_fallback_outfit"])
                        st.info(t[lang]["ai_target"].format(u=tt, a=tb))
                        st.success(t[lang]["success_outfit"])
                        c1, c2, c3 = st.columns(3)
                        
                        c1.markdown(t[lang]["opt1"])
                        c1.markdown(f"{t[lang]['top']} {render_top(bt1['ic'], bt1['dis'], used_under)}")
                        c1.markdown(f"{t[lang]['bottom']} {render_bot(bb1['ic'], bb1['dis'])}")
                        
                        c2.markdown(t[lang]["opt2"])
                        c2.markdown(f"{t[lang]['top']} {render_top(bt2['ic'], bt2['dis'], used_under)}")
                        c2.markdown(f"{t[lang]['bottom']} {render_bot(bb2['ic'], bb2['dis'])}")
                        
                        c3.markdown(t[lang]["opt3"])
                        c3.markdown(f"{t[lang]['top']} {render_top(at['ic'], at['dis'], used_under)}")
                        c3.markdown(f"{t[lang]['bottom']} {render_bot(ab['ic'], ab['dis'])}")
                        
                        if accs:
                            st.markdown("---")
                            st.markdown(f"{t[lang]['extra']} {', '.join(accs)}")
                    else: st.warning(t[lang]["err_outfit"])

with tab2:
    st.markdown("### " + t[lang]["tab2"])
    time_opts = ["Morning", "Afternoon", "Evening"]
    time_opts_ui = time_opts if lang == "en" else ["Sabah (09:00)", "Öğlen (15:00)", "Akşam (21:00)"]
    sel_t = st.radio(t[lang]["plan_time_lbl"], time_opts_ui, horizontal=True)
    sel_t_ml = time_opts[time_opts_ui.index(sel_t)]
    
    if city and st.button(t[lang]["btn_plan"], type="primary"):
        with st.spinner(t[lang]["ai_calc"]):
            ok, days = get_5_day_forecast(city, sel_t_ml, lang)
            if ok:
                cols = st.columns(len(days))
                for idx, day in enumerate(days):
                    with cols[idx]:
                        st.markdown(f"**🗓️ {day['date']}**")
                        st.caption(f"🕒 {day['time']} | {day['desc']}")
                        st.write(f"🌡️ {day['temp']:.1f}°C (His: {day['feels_like']:.1f}°C)")
                        
                        ban_s = day['feels_like'] < 19 or day['precip'] in ["Rain", "Snow"]
                        
                        ok2, out = generate_outfit(day['feels_like'], day['precip'], day['wind'], sel_t_ml, owned_tops, owned_bots, owned_accs, has_umbrella, has_undershirt, layering_needed=False, ban_shorts=ban_s)
                        st.markdown("---")
                        if ok2:
                            tt, tb, bt1, bb1, bt2, bb2, at, ab, accs, used_under, used_fallback = out
                            
                            st.write("👕 " + render_top(bt1['ic'], bt1['dis'], used_under))
                            st.write("👖 " + render_bot(bb1['ic'], bb1['dis']))
                            if accs: st.write("🧣 *" + ", ".join(accs) + "*")
                            if used_fallback:
                                st.caption("*(Alternatif Parçalar)*")
                        else:
                            st.write("⚠️ " + t[lang]["err_outfit"])
