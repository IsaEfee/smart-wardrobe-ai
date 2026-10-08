import streamlit as st
import pandas as pd
import joblib
import random
import os
import requests
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Wardrobe Assistant", page_icon="🧥", layout="wide", initial_sidebar_state="expanded")

API_KEY = "3795ac331def1d702f917c283a417051"

# --- TRANSLATION DICTIONARY ---
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
        "wt1": "👕 Inner Tops", "wt2": "🧥 Outerwear", "wt3": "👖 Bottoms", "wt4": "🧦 Hosiery / Thermals",
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
        "opt1": "### 👕 Option 1 (Everyday)", "opt2": "### 🧥 Option 2 (Alternative)",
        "top": "**Top:**", "bottom": "**Bottom:**",
        "err_outfit": "⚠️ Couldn't find a perfect match in your wardrobe for these specific conditions!",
        "none_top": "None (Innerwear Only)", "none_bottom": "None (Underwear Only)",
        "rain": "Rain", "snow": "Snow", "clear": "Clear"
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
        "wt1": "👕 Üst İç Giyim", "wt2": "🧥 Dış Giyim", "wt3": "👖 Alt Giyim", "wt4": "🧦 İçlik ve Çorap",
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
        "ai_calc": "Yapay zeka ideal yalıtım hedeflerini hesaplıyor...",
        "ai_target": "🧠 **Yapay Zeka Hedefi:** Üst: **{u:.1f} CLO**, Alt: **{a:.1f} CLO**",
        "success_outfit": "✅ **Sana Özel Kombin Önerileri:**",
        "opt1": "### 👕 Seçenek 1 (Günlük)", "opt2": "### 🧥 Seçenek 2 (Alternatif)",
        "top": "**Üst:**", "bottom": "**Alt:**",
        "err_outfit": "⚠️ Dolabındaki kıyafetlerle bu hava şartlarına tam uygun bir kombin bulamadım!",
        "none_top": "Yok (Sadece İç Giyim)", "none_bottom": "Yok (Sadece İç Çamaşırı)",
        "rain": "Yağmur", "snow": "Kar", "clear": "Yok"
    }
}

# --- BILINGUAL DATABASE ---
kiyafet_db = {
    "top_inner": [
        {"en": "Tank Top / Crop Top", "tr": "Askılı Bluz / Crop Top", "clo": 0.10, "gender": ["Female"], "basic": True, "hoodie": False},
        {"en": "Undershirt", "tr": "Atlet", "clo": 0.10, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Short Sleeve T-Shirt", "tr": "Kısa Kollu Tişört", "clo": 0.15, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Elegant Blouse", "tr": "Şık Bluz", "clo": 0.20, "gender": ["Female"], "basic": False, "hoodie": False},
        {"en": "Shirt", "tr": "Gömlek", "clo": 0.20, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Long Sleeve T-Shirt", "tr": "Uzun Kollu Tişört", "clo": 0.25, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Flannel / Thick Shirt", "tr": "Oduncu Gömleği / Kalın Gömlek", "clo": 0.30, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
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
        {"en": "Cardigan", "tr": "Hırka", "clo": 0.30, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Blazer", "tr": "Blazer Ceket", "clo": 0.35, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Denim Jacket", "tr": "Kot Ceket", "clo": 0.35, "gender": ["Female", "Male"], "basic": True, "hoodie": False},
        {"en": "Trench Coat", "tr": "Trençkot", "clo": 0.40, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Leather Jacket", "tr": "Deri Ceket", "clo": 0.45, "gender": ["Female", "Male"], "basic": False, "hoodie": False},
        {"en": "Winter Puffer Jacket", "tr": "Kışlık Şişme Mont", "clo": 0.80, "gender": ["Female", "Male"], "basic": True, "hoodie": True},
        {"en": "Faux Fur Coat", "tr": "Peluş Kaban", "clo": 0.90, "gender": ["Female"], "basic": False, "hoodie": False},
        {"en": "Thick Wool Coat", "tr": "Kalın Yün Kaban", "clo": 1.00, "gender": ["Female", "Male"], "basic": False, "hoodie": False}
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
        {"en": "Shorts", "tr": "Şort", "clo": 0.15, "gender": ["Female", "Male"], "basic": True},
        {"en": "Tights (Sport/Thin)", "tr": "Tayt (Spor / İnce)", "clo": 0.15, "gender": ["Female"], "basic": True},
        {"en": "Linen Pants", "tr": "Keten Pantolon", "clo": 0.20, "gender": ["Female", "Male"], "basic": True},
        {"en": "Thin Fabric Pants", "tr": "İnce Kumaş Pantolon", "clo": 0.20, "gender": ["Female", "Male"], "basic": False},
        {"en": "Maxi (Long) Skirt", "tr": "Maksi (Uzun) Etek", "clo": 0.25, "gender": ["Female"], "basic": False},
        {"en": "Jeans", "tr": "Kot Pantolon", "clo": 0.30, "gender": ["Female", "Male"], "basic": True},
        {"en": "Cargo Pants", "tr": "Kargo Pantolon", "clo": 0.30, "gender": ["Female", "Male"], "basic": False},
        {"en": "Sweatpants", "tr": "Eşofman Altı", "clo": 0.35, "gender": ["Female", "Male"], "basic": True},
        {"en": "Fleece-Lined Winter Tights", "tr": "İçi Polarlı Kışlık Tayt", "clo": 0.35, "gender": ["Female"], "basic": True},
        {"en": "Thick Corduroy Pants", "tr": "Kalın Kadife Pantolon", "clo": 0.50, "gender": ["Female", "Male"], "basic": False}
    ]
}

# --- SESSION STATE ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = "en"
if 'onboarding_complete' not in st.session_state:
    st.session_state['onboarding_complete'] = False
if 'ml_gender' not in st.session_state:
    st.session_state['ml_gender'] = "Female"
if 'ml_profile' not in st.session_state:
    st.session_state['ml_profile'] = "Standard"

# --- ONBOARDING FORM ---
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
            st.subheader(t[lang]["q1"])
            cins_ui = st.radio(t[lang]["gender_lbl"], [t[lang]["female"], t[lang]["male"]])
            
            st.subheader(t[lang]["q2"])
            prof_ui = st.selectbox(t[lang]["prof_lbl"], [t[lang]["cold"], t[lang]["std"], t[lang]["hot"]])
            
            submitted = st.form_submit_button(t[lang]["btn_save"], use_container_width=True)
            
            if submitted:
                st.session_state['ml_gender'] = "Female" if cins_ui == t[lang]["female"] else "Male"
                if prof_ui == t[lang]["cold"]: st.session_state['ml_profile'] = "Cold-natured"
                elif prof_ui == t[lang]["hot"]: st.session_state['ml_profile'] = "Hot-blooded"
                else: st.session_state['ml_profile'] = "Standard"
                
                st.session_state['onboarding_complete'] = True
                st.rerun()
    st.stop()
else:
    lang = st.session_state['lang']

# ==========================================
# MAIN APP
# ==========================================

@st.cache_resource
def load_model():
    file_path = os.path.join(os.path.dirname(__file__), "wardrobe_model.pkl")
    if not os.path.exists(file_path): return None, None
    data = joblib.load(file_path)
    return data['model'], data['encoders']

model, encoders = load_model()

def get_live_weather(city, lang):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang={lang}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            wind = data["wind"]["speed"] * 3.6
            weather_main = data["weather"][0]["main"]
            desc = data["weather"][0]["description"].title()
            
            if weather_main in ["Rain", "Drizzle", "Thunderstorm"]: precip_ml = "Rain"
            elif weather_main == "Snow": precip_ml = "Snow"
            else: precip_ml = "Clear"
            
            timezone_offset = data.get("timezone", 0)
            city_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=timezone_offset)
            city_hour = city_time.hour
            city_time_str = city_time.strftime("%H:%M")
                
            return True, (temp, feels_like, precip_ml, wind, desc, city_hour, city_time_str)
        else:
            return False, f"API Error: {response.json().get('message', 'Error')}"
    except Exception as e:
        return False, str(e)

st.title(t[lang]["title"])

if model is None:
    st.error(t[lang]["err_model"])
    st.stop()

# Sidebar
st.sidebar.header(t[lang]["prof_title"])
ml_gen = st.session_state['ml_gender']
ml_prof = st.session_state['ml_profile']

ui_gen = t[lang]["female"] if ml_gen == "Female" else t[lang]["male"]
ui_prof = t[lang]["cold"] if ml_prof == "Cold-natured" else (t[lang]["hot"] if ml_prof == "Hot-blooded" else t[lang]["std"])

st.sidebar.success(f"**{t[lang]['gender_lbl']}:** {ui_gen}  \n**{t[lang]['prof_lbl']}:** {ui_prof}")
if st.sidebar.button(t[lang]["btn_edit"]):
    st.session_state['onboarding_complete'] = False
    st.rerun()

st.sidebar.markdown("---")
has_umbrella = st.sidebar.checkbox(t[lang]["umbrella"])

st.sidebar.markdown("---")
st.sidebar.header(t[lang]["wardrobe_title"])
st.sidebar.markdown(t[lang]["wardrobe_desc"])

top_inners = [x[lang] for x in kiyafet_db["top_inner"]]
top_outers = [x[lang] for x in kiyafet_db["top_outer"] if x["en"] != "None (Innerwear Only)"]
bottom_outers = [x[lang] for x in kiyafet_db["bottom_outer"]]
bottom_inners = [x[lang] for x in kiyafet_db["bottom_inner"] if x["en"] != "None (Underwear Only)"]

def_ti_en = ["Short Sleeve T-Shirt", "Shirt", "Thin Knit Sweater", "Hoodie"]
def_to_en = ["Thin Windbreaker", "Cardigan", "Winter Puffer Jacket"]
def_bo_en = ["Jeans", "Sweatpants", "Tights (Sport/Thin)", "Shorts"] if ml_gen == "Female" else ["Jeans", "Sweatpants", "Shorts"]

def_ti_ui = [next(x[lang] for x in kiyafet_db["top_inner"] if x["en"] == e) for e in def_ti_en]
def_to_ui = [next(x[lang] for x in kiyafet_db["top_outer"] if x["en"] == e) for e in def_to_en]
def_bo_ui = [next(x[lang] for x in kiyafet_db["bottom_outer"] if x["en"] == e) for e in def_bo_en]

sel_top_inner, sel_top_outer, sel_bottom_outer, sel_bottom_inner = [], [], [], []

with st.sidebar.expander(t[lang]["wt1"], expanded=False):
    st.markdown(f"**{t[lang]['what_do_u_have']}**")
    for i, item in enumerate(top_inners):
        if st.checkbox(item, value=(item in def_ti_ui), key=f"ti_{i}"): sel_top_inner.append(item)

with st.sidebar.expander(t[lang]["wt2"], expanded=False):
    st.markdown(f"**{t[lang]['what_do_u_have']}**")
    for i, item in enumerate(top_outers):
        if st.checkbox(item, value=(item in def_to_ui), key=f"to_{i}"): sel_top_outer.append(item)

with st.sidebar.expander(t[lang]["wt3"], expanded=False):
    st.markdown(f"**{t[lang]['what_do_u_have']}**")
    for i, item in enumerate(bottom_outers):
        if st.checkbox(item, value=(item in def_bo_ui), key=f"bo_{i}"): sel_bottom_outer.append(item)

with st.sidebar.expander(t[lang]["wt4"], expanded=False):
    st.markdown(f"**{t[lang]['what_do_u_have']}**")
    for i, item in enumerate(bottom_inners):
        if st.checkbox(item, value=False, key=f"bi_{i}"): sel_bottom_inner.append(item)

owned_tops = sel_top_inner + sel_top_outer
owned_bottoms = sel_bottom_outer + sel_bottom_inner

owned_tops.append(t[lang]["none_top"])
owned_bottoms.append(t[lang]["none_bottom"])

# Main Panel
popular_cities = ["Istanbul", "Ankara", "Izmir", "London", "New York", "Paris", "Tokyo", "Berlin", t[lang]["city_other"]]
selected_list = st.selectbox(t[lang]["city_lbl"], popular_cities)

if selected_list == t[lang]["city_other"]:
    city = st.text_input(t[lang]["city_type"], "Seattle")
else:
    city = selected_list

temp_c, feels_like_c, precip_ml, wind_kmh, time_ml = 15.0, 15.0, "Clear", 5.0, "Afternoon"
city_time_str = "--:--"

if city:
    success, result = get_live_weather(city, lang)
    if success:
        temp_c, feels_like_c, precip_ml, wind_kmh, desc, city_hour, city_time_str = result
        
        if 5 <= city_hour < 12: time_ml = "Morning"
        elif 12 <= city_hour < 18: time_ml = "Afternoon"
        else: time_ml = "Evening"
        
        st.success(t[lang]["live_success"])
        m1, m2, m3, m4 = st.columns(4)
        
        feels_txt = f"Feels: {feels_like_c:.1f}°C" if lang == "en" else f"Hissedilen: {feels_like_c:.1f}°C"
        m1.metric(t[lang]["temp"], f"{temp_c:.1f} °C", feels_txt, delta_color="off")
        
        time_ui = time_ml
        if lang == "tr":
            time_ui = "Sabah" if time_ml == "Morning" else ("Öğlen" if time_ml == "Afternoon" else "Akşam/Gece")
        
        m2.metric(t[lang]["cond"], f"{desc}", f"{city_time_str} - {time_ui}", delta_color="off")
        
        ui_precip = t[lang]["rain"] if precip_ml == "Rain" else (t[lang]["snow"] if precip_ml == "Snow" else t[lang]["clear"])
        m3.metric(t[lang]["precip"], f"{ui_precip}")
        m4.metric(t[lang]["wind"], f"{wind_kmh:.1f} km/h")
    else:
        st.warning(f"{t[lang]['wait_conn']} {result}")

with st.expander(t[lang]["manual_mode"]):
    col1, col2, col3, col4 = st.columns(4)
    with col1: man_temp = st.slider(t[lang]["temp"] + " (°C)", -5.0, 30.0, float(feels_like_c))
    
    precip_opts_ml = ["Clear", "Rain", "Snow"]
    precip_opts_ui = [t[lang]["clear"], t[lang]["rain"], t[lang]["snow"]]
    with col2: man_precip_ui = st.selectbox(t[lang]["precip"], precip_opts_ui, index=precip_opts_ml.index(precip_ml))
    with col3: man_wind = st.slider(t[lang]["wind"] + " (km/h)", 0.0, 30.0, float(wind_kmh))
    
    time_opts_ml = ["Morning", "Afternoon", "Evening"]
    time_opts_ui = ["Sabah", "Öğlen", "Akşam/Gece"] if lang == "tr" else time_opts_ml
    with col4: man_time_ui = st.selectbox("Zaman / Time", time_opts_ui, index=time_opts_ml.index(time_ml))
        
    man_precip_ml = precip_opts_ml[precip_opts_ui.index(man_precip_ui)]
    man_time_ml = time_opts_ml[time_opts_ui.index(man_time_ui)]
    
    if man_temp != feels_like_c or man_precip_ml != precip_ml or man_wind != wind_kmh or man_time_ml != time_ml:
        temp_c, feels_like_c, precip_ml, wind_kmh, time_ml = man_temp, man_temp, man_precip_ml, man_wind, man_time_ml
        st.info(t[lang]["manual_active"])

st.markdown("---")

if st.button(t[lang]["btn_suggest"], type="primary"):
    with st.spinner(t[lang]["ai_calc"]):
        target_top, target_bottom = None, None
        gen_enc = encoders['gender'].transform([ml_gen])[0]
        prof_enc = encoders['profile'].transform([ml_prof])[0]
        precip_enc = encoders['precip'].transform([precip_ml])[0]
        time_enc = encoders['time'].transform([time_ml])[0]
        comfortable_enc = encoders['outcome'].transform(['Comfortable'])[0]
        
        valid_targets = []
        for u in [x * 0.1 for x in range(2, 20)]: 
            for a in [x * 0.1 for x in range(1, 10)]: 
                if a > u + 0.1: continue
                # Yaz modası kuralları artık hissedilen sıcaklığa (feels_like_c) göre
                if feels_like_c > 12 and (u - a) > 0.2: continue
                
                # YENİ 8 PARAMETRELİ TAHMİN FONKSİYONU (Faz-2)
                if model.predict([[gen_enc, prof_enc, feels_like_c, precip_enc, wind_kmh, time_enc, u, a]])[0] == comfortable_enc:
                    valid_targets.append((u, a))
                    
        if valid_targets:
            target_top = sum([h[0] for h in valid_targets]) / len(valid_targets)
            target_bottom = sum([h[1] for h in valid_targets]) / len(valid_targets)
        else:
            target_top = 2.0 if feels_like_c < 5 else 0.2
            target_bottom = 1.0 if feels_like_c < 5 else 0.1
            
        st.info(t[lang]["ai_target"].format(u=target_top, a=target_bottom))

        suitable_tops = []
        for ic in kiyafet_db["top_inner"]:
            for dis in kiyafet_db["top_outer"]:
                if ic[lang] not in owned_tops or dis[lang] not in owned_tops: continue
                if ml_gen not in ic["gender"] or ml_gen not in dis["gender"]: continue
                if precip_ml in ["Rain", "Snow"] and not has_umbrella and not (ic["hoodie"] or dis["hoodie"]): continue 
                
                # KURAL: 19 derecenin altında sadece kısa kollu ile dışarı çıkılmaz!
                is_short_sleeve = ic["en"] in ["Short Sleeve T-Shirt", "Tank Top / Crop Top", "Undershirt", "Elegant Blouse"]
                is_no_outer = dis["en"] == "None (Innerwear Only)"
                if feels_like_c < 19 and is_short_sleeve and is_no_outer:
                    continue
                
                if abs((ic["clo"] + dis["clo"]) - target_top) <= 0.15:
                    suitable_tops.append({"ic_name": ic[lang], "dis_name": dis[lang], "basic": ic["basic"] and dis["basic"]})
                    
        suitable_bottoms = []
        for ic_alt in kiyafet_db["bottom_inner"]:
            for dis_alt in kiyafet_db["bottom_outer"]:
                if ic_alt[lang] not in owned_bottoms or dis_alt[lang] not in owned_bottoms: continue
                if ml_gen not in ic_alt["gender"] or ml_gen not in dis_alt["gender"]: continue
                if precip_ml in ["Rain", "Snow"] and "Shorts" in dis_alt["en"]: continue
                
                # KURAL: 20 derecenin altında şort giyilmez!
                if feels_like_c < 20 and "Shorts" in dis_alt["en"]: continue
                if dis_alt["en"] == "Shorts" and ic_alt["en"] != "None (Underwear Only)": continue
                
                if abs((ic_alt["clo"] + dis_alt["clo"]) - target_bottom) <= 0.15:
                    suitable_bottoms.append({"ic_name": ic_alt[lang], "dis_name": dis_alt[lang], "basic": ic_alt["basic"] and dis_alt["basic"]})

        if suitable_tops and suitable_bottoms:
            basic_top = next((x for x in suitable_tops if x["basic"]), suitable_tops[0])
            basic_bottom = next((x for x in suitable_bottoms if x["basic"]), suitable_bottoms[0])
            alt_top = random.choice([x for x in suitable_tops if x != basic_top] or [basic_top])
            alt_bottom = random.choice([x for x in suitable_bottoms if x != basic_bottom] or [basic_bottom])
            
            st.success(t[lang]["success_outfit"])
            def format_text(ic, dis, empty_word): return dis if ic == empty_word else f"{dis} + {ic}"
            
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.markdown(t[lang]["opt1"])
                st.write(t[lang]["top"], format_text(basic_top['dis_name'], basic_top['ic_name'], t[lang]["none_top"]))
                st.write(t[lang]["bottom"], format_text(basic_bottom['ic_name'], basic_bottom['dis_name'], t[lang]["none_bottom"]))
            with r_col2:
                st.markdown(t[lang]["opt2"])
                st.write(t[lang]["top"], format_text(alt_top['dis_name'], alt_top['ic_name'], t[lang]["none_top"]))
                st.write(t[lang]["bottom"], format_text(alt_bottom['ic_name'], alt_bottom['dis_name'], t[lang]["none_bottom"]))
        else:
            st.warning(t[lang]["err_outfit"])
