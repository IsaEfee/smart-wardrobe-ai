import streamlit as st
import pandas as pd
import joblib
import random
import os
import requests
import datetime

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
        "opt1": "### 👕 Option 1", "opt2": "### 🧥 Option 2",
        "top": "**Top:**", "bottom": "**Bottom:**", "extra": "**➕ Extras:**",
        "err_outfit": "⚠️ Couldn't find a perfect match in your wardrobe for these specific conditions!",
        "none_top": "None (Innerwear Only)", "none_bottom": "None (Underwear Only)",
        "rain": "Rain", "snow": "Snow", "clear": "Clear",
        "tab1": "⏳ Right Now", "tab2": "📅 5-Day Planner",
        "plan_time_lbl": "Select time for daily forecast:",
        "btn_plan": "Generate 5-Day Plan 🗓️"
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
        "opt1": "### 👕 Seçenek 1", "opt2": "### 🧥 Seçenek 2",
        "top": "**Üst:**", "bottom": "**Alt:**", "extra": "**➕ Ekstra:**",
        "err_outfit": "⚠️ Dolabındaki kıyafetlerle tam uygun kombin bulunamadı!",
        "none_top": "Yok (Sadece İç Giyim)", "none_bottom": "Yok (Sadece İç Çamaşırı)",
        "rain": "Yağmur", "snow": "Kar", "clear": "Yok",
        "tab1": "⏳ Şu An", "tab2": "📅 5 Günlük Planlayıcı",
        "plan_time_lbl": "Tahminlerin Hangi Saat İçin Yapılmasını İstersin?",
        "btn_plan": "5 Günlük Plan Oluştur 🗓️"
    }
}

kiyafet_db = {
    "top_inner": [
        {"en": "Tank Top / Crop Top", "tr": "Askılı Bluz / Crop Top", "clo": 0.10, "gender": ["Female"], "basic": True, "hoodie": False},
        {"en": "Undershirt", "tr": "Atlet", "clo": 0.10, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Short Sleeve T-Shirt", "tr": "Kısa Kollu Tişört", "clo": 0.15, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Polo T-Shirt", "tr": "Polo Yaka Tişört", "clo": 0.17, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Elegant Blouse", "tr": "Şık Bluz", "clo": 0.20, "gender": ["Female"], "basic": False, "hoodie": False},
        {"en": "Shirt", "tr": "Gömlek", "clo": 0.20, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Long Sleeve T-Shirt", "tr": "Uzun Kollu Tişört", "clo": 0.25, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Flannel / Thick Shirt", "tr": "Oduncu Gömleği", "clo": 0.30, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Thin Knit Sweater", "tr": "İnce Triko Kazak", "clo": 0.35, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Hoodie", "tr": "Kapşonlu Sweatshirt", "clo": 0.40, "gender": ["Female", "Male"], "basic": True, "hoodie": True},
        {"en": "Quarter-Zip Fleece", "tr": "Yarım Fermuarlı Polar", "clo": 0.45, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Turtleneck Sweater", "tr": "Boğazlı Kazak", "clo": 0.50, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Thick Wool Sweater", "tr": "Kalın Yün Kazak", "clo": 0.60, "gender": ["Female", "Male"], "basic": False, "hoodie": False}
    ],
    "top_outer": [
        {"en": "None (Innerwear Only)", "tr": "Yok (Sadece İç Giyim)", "clo": 0.0, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Hooded Raincoat", "tr": "Kapüşonlu Yağmurluk", "clo": 0.20, "gender": ["Female", "Male"], "basic": True, "hoodie": True},
        {"en": "Thin Windbreaker", "tr": "İnce Rüzgarlık", "clo": 0.25, "gender": ["Female", "Male"], "basic": True, "hoodie": True},
        {"en": "Puffer Vest", "tr": "Şişme Yelek", "clo": 0.25, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Cardigan", "tr": "Hırka", "clo": 0.30, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Blazer", "tr": "Blazer Ceket", "clo": 0.35, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Denim Jacket", "tr": "Kot Ceket", "clo": 0.35, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Trench Coat", "tr": "Trençkot", "clo": 0.40, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Leather Jacket", "tr": "Deri Ceket", "clo": 0.45, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Winter Puffer Jacket", "tr": "Kışlık Şişme Mont", "clo": 0.80, "gender": ["Female", "Male"], "basic": True, "hoodie": True},
        {"en": "Faux Fur Coat", "tr": "Peluş Kaban", "clo": 0.90, "gender": ["Female"], "basic": False, "hoodie": False},
        {"en": "Thick Wool Coat", "tr": "Kalın Yün Kaban", "clo": 1.00, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Heavy Overcoat", "tr": "Ağır Kışlık Palto", "clo": 1.20, "gender": ["Female", "Male"], "basic": False, "hoodie": False}
    ],
    "bottom_inner": [
        {"en": "None (Underwear Only)", "tr": "Yok (Sadece İç Çamaşırı)", "clo": 0.0, "gender": ["Female", "Male"], "basic": True},
        {"en": "Fishnet/Patterned Tights", "tr": "File/Desenli Külotlu Çorap", "clo": 0.05, "gender": ["Female"], "basic": False},
        {"en": "Thin Tights", "tr": "İnce Külotlu Çorap", "clo": 0.10, "gender": ["Female"], "basic": True},
        {"en": "Thick Thermal Tights", "tr": "Kalın Termal Çorap", "clo": 0.25, "gender": ["Female"], "basic": False},
        {"en": "Thermal Underwear", "tr": "Termal İçlik", "clo": 0.30, "gender": ["Female", "Male"], "basic": False}
    ],
    "bottom_outer": [
        {"en": "Mini Skirt", "tr": "Kısa Etek (Mini)", "clo": 0.10, "gender": ["Female"], "basic": False},
        {"en": "Pleated Skirt", "tr": "Pileli Etek", "clo": 0.15, "gender": ["Female"], "basic": False},
        {"en": "Shorts", "tr": "Şort", "clo": 0.15, "gender": ["Female", "Male"], "basic": True},
        {"en": "Tights (Sport/Thin)", "tr": "Tayt (Spor / İnce)", "clo": 0.15, "gender": ["Female"], "basic": True},
        {"en": "Linen Pants", "tr": "Keten Pantolon", "clo": 0.20, "gender": ["Female", "Male"], "basic": True},
        {"en": "Thin Fabric Pants", "tr": "İnce Kumaş Pantolon", "clo": 0.20, "gender": ["Female", "Male"], "basic": False},
        {"en": "Maxi (Long) Skirt", "tr": "Maksi (Uzun) Etek", "clo": 0.25, "gender": ["Female"], "basic": False},
        {"en": "Chino Pants", "tr": "Chino / Kumaş Pantolon", "clo": 0.25, "gender": ["Female", "Male"], "basic": True},
        {"en": "Jeans", "tr": "Kot Pantolon", "clo": 0.30, "gender": ["Female", "Male"], "basic": True},
        {"en": "Cargo Pants", "tr": "Kargo Pantolon", "clo": 0.30, "gender": ["Female", "Male"], "basic": False},
        {"en": "Sweatpants", "tr": "Eşofman Altı", "clo": 0.35, "gender": ["Female", "Male"], "basic": True},
        {"en": "Fleece-Lined Winter Tights", "tr": "İçi Polarlı Kışlık Tayt", "clo": 0.35, "gender": ["Female"], "basic": True},
        {"en": "Fleece Joggers", "tr": "Kışlık Kalın Eşofman", "clo": 0.45, "gender": ["Female", "Male"], "basic": True},
        {"en": "Thick Corduroy Pants", "tr": "Kalın Kadife Pantolon", "clo": 0.50, "gender": ["Female", "Male"], "basic": False}
    ],
    "accessories": [
        {"en": "Sunglasses", "tr": "Güneş Gözlüğü", "gender": ["Female", "Male"], "basic": True},
        {"en": "Beanie (Hat)", "tr": "Bere", "gender": ["Female", "Male"], "basic": True},
        {"en": "Scarf", "tr": "Atkı", "gender": ["Female", "Male"], "basic": True},
        {"en": "Leather/Winter Gloves", "tr": "Kışlık Eldiven", "gender": ["Female", "Male"], "basic": True}
    ]
}

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

def generate_outfit(feels_like_c, precip_ml, wind_kmh, time_ml, owned_tops, owned_bottoms, owned_accs, has_umbrella):
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
        
    s_tops, s_bots = [], []
    for ic in kiyafet_db["top_inner"]:
        for dis in kiyafet_db["top_outer"]:
            if ic[lang] not in owned_tops or dis[lang] not in owned_tops: continue
            if st.session_state['ml_gender'] not in ic["gender"] or st.session_state['ml_gender'] not in dis["gender"]: continue
            if precip_ml in ["Rain", "Snow"] and not has_umbrella and not (ic["hoodie"] or dis["hoodie"]): continue 
            is_no = dis["en"] == "None (Innerwear Only)"
            if feels_like_c < 19 and ic["en"] in ["Short Sleeve T-Shirt", "Tank Top / Crop Top", "Undershirt", "Elegant Blouse", "Polo T-Shirt"] and is_no: continue
            if feels_like_c < 22 and wind_kmh > 15 and is_no: continue
            if abs((ic["clo"] + dis["clo"]) - tt) <= 0.15:
                s_tops.append({"ic": ic[lang], "dis": dis[lang], "basic": ic["basic"] and dis["basic"]})
                
    for ic in kiyafet_db["bottom_inner"]:
        for dis in kiyafet_db["bottom_outer"]:
            if ic[lang] not in owned_bottoms or dis[lang] not in owned_bottoms: continue
            if st.session_state['ml_gender'] not in ic["gender"] or st.session_state['ml_gender'] not in dis["gender"]: continue
            if precip_ml in ["Rain", "Snow"] and "Shorts" in dis["en"]: continue
            if feels_like_c < 20 and "Shorts" in dis["en"]: continue
            if dis["en"] == "Shorts" and ic["en"] != "None (Underwear Only)": continue
            if abs((ic["clo"] + dis["clo"]) - tb) <= 0.15:
                s_bots.append({"ic": ic[lang], "dis": dis[lang], "basic": ic["basic"] and dis["basic"]})
                
    # Aksesuar Kural Motoru (Smart Add-ons)
    accs = []
    if precip_ml == "Clear" and time_ml in ["Morning", "Afternoon"] and feels_like_c > 15:
        sun_lbl = "Sunglasses" if lang == "en" else "Güneş Gözlüğü"
        if sun_lbl in owned_accs: accs.append(sun_lbl)
        
    if feels_like_c < 10:
        hat_lbl = "Beanie (Hat)" if lang == "en" else "Bere"
        scarf_lbl = "Scarf" if lang == "en" else "Atkı"
        if hat_lbl in owned_accs: accs.append(hat_lbl)
        if scarf_lbl in owned_accs: accs.append(scarf_lbl)
        
    if feels_like_c < 5:
        glove_lbl = "Leather/Winter Gloves" if lang == "en" else "Kışlık Eldiven"
        if glove_lbl in owned_accs: accs.append(glove_lbl)

    if s_tops and s_bots:
        bt = next((x for x in s_tops if x["basic"]), s_tops[0])
        bb = next((x for x in s_bots if x["basic"]), s_bots[0])
        at = random.choice([x for x in s_tops if x != bt] or [bt])
        ab = random.choice([x for x in s_bots if x != bb] or [bb])
        return True, (tt, tb, bt, bb, at, ab, accs)
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

st.sidebar.header(t[lang]["wardrobe_title"])
top_inners = [x[lang] for x in kiyafet_db["top_inner"]]
top_outers = [x[lang] for x in kiyafet_db["top_outer"] if x["en"] != "None (Innerwear Only)"]
bottom_outers = [x[lang] for x in kiyafet_db["bottom_outer"]]
bottom_inners = [x[lang] for x in kiyafet_db["bottom_inner"] if x["en"] != "None (Underwear Only)"]
acc_items = [x[lang] for x in kiyafet_db["accessories"]]

def_ti = [next(x[lang] for x in kiyafet_db["top_inner"] if x["en"] == e) for e in ["Short Sleeve T-Shirt", "Shirt", "Thin Knit Sweater", "Hoodie"]]
def_to = [next(x[lang] for x in kiyafet_db["top_outer"] if x["en"] == e) for e in ["Thin Windbreaker", "Cardigan", "Winter Puffer Jacket"]]
def_bo = [next(x[lang] for x in kiyafet_db["bottom_outer"] if x["en"] == e) for e in (["Jeans", "Sweatpants", "Tights (Sport/Thin)", "Shorts"] if st.session_state['ml_gender'] == "Female" else ["Jeans", "Sweatpants", "Shorts"])]
def_ac = [next(x[lang] for x in kiyafet_db["accessories"] if x["en"] == e) for e in ["Beanie (Hat)", "Scarf", "Leather/Winter Gloves", "Sunglasses"]]

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

owned_tops = s_ti + s_to + [t[lang]["none_top"]]
owned_bots = s_bo + s_bi + [t[lang]["none_bottom"]]
owned_accs = s_ac

cities = ["Istanbul", "Ankara", "Izmir", "London", "New York", "Paris", "Tokyo", "Berlin", t[lang]["city_other"]]
sel_city = st.selectbox(t[lang]["city_lbl"], cities)
city = st.text_input(t[lang]["city_type"], "Seattle") if sel_city == t[lang]["city_other"] else sel_city

tab1, tab2 = st.tabs([t[lang]["tab1"], t[lang]["tab2"]])

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
            
            if st.button(t[lang]["btn_suggest"], type="primary", key="btn_now"):
                with st.spinner(t[lang]["ai_calc"]):
                    ok, out = generate_outfit(flc, p_ml, w_kmh, tml, owned_tops, owned_bots, owned_accs, has_umbrella)
                    if ok:
                        tt, tb, bt, bb, at, ab, accs = out
                        st.info(t[lang]["ai_target"].format(u=tt, a=tb))
                        st.success(t[lang]["success_outfit"])
                        c1, c2 = st.columns(2)
                        f_txt = lambda i,d: d if i==t[lang]["none_top"] or i==t[lang]["none_bottom"] else f"{d} + {i}"
                        c1.markdown(t[lang]["opt1"]); c1.write(t[lang]["top"], f_txt(bt['ic'], bt['dis'])); c1.write(t[lang]["bottom"], f_txt(bb['ic'], bb['dis']))
                        c2.markdown(t[lang]["opt2"]); c2.write(t[lang]["top"], f_txt(at['ic'], at['dis'])); c2.write(t[lang]["bottom"], f_txt(ab['ic'], ab['dis']))
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
                        
                        ok2, out = generate_outfit(day['feels_like'], day['precip'], day['wind'], sel_t_ml, owned_tops, owned_bots, owned_accs, has_umbrella)
                        st.markdown("---")
                        if ok2:
                            tt, tb, bt, bb, at, ab, accs = out
                            f_txt = lambda i,d: d if i==t[lang]["none_top"] or i==t[lang]["none_bottom"] else f"{d} + {i}"
                            st.write("👕 " + f_txt(bt['ic'], bt['dis']))
                            st.write("👖 " + f_txt(bb['ic'], bb['dis']))
                            if accs: st.write("🧣 *" + ", ".join(accs) + "*")
                        else:
                            st.write("⚠️ " + t[lang]["err_outfit"])
            else: st.error(days)
