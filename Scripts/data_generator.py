import pandas as pd
import random
import os

def generate_final_data(num_rows=5000):
    data = []
    profiles = ["Cold-natured", "Standard", "Hot-blooded"]
    genders = ["Female", "Male"]
    times_of_day = ["Morning", "Afternoon", "Evening"]
    
    for _ in range(num_rows):
        # Gerçek sıcaklık yerine doğrudan Hissedilen Sıcaklık üzerinden üretiyoruz
        feels_like_c = random.uniform(-5, 30)
        wind_kmh = random.uniform(0, 30) 
        time_of_day = random.choice(times_of_day)
        
        if feels_like_c <= 3:
            precip = random.choices(["Clear", "Rain", "Snow"], weights=[60, 15, 25])[0]
        else:
            precip = random.choices(["Clear", "Rain"], weights=[70, 30])[0]
            
        profile = random.choice(profiles)
        gender = random.choice(genders)
        
        # Clothing CLO Values
        top_clo = round(random.uniform(0.1, 2.0), 2)
        bottom_clo = round(random.uniform(0.1, 1.0), 2)
        total_clo = top_clo + bottom_clo
        
        # --- SCIENTIFIC IDEAL CLO CALCULATION (USING FEELS LIKE) ---
        # Artık rüzgar soğuğunu (wind chill) formüle eklemiyoruz çünkü feels_like zaten bunu içeriyor.
        ideal_clo = max(0.1, (22 - feels_like_c) * 0.10)
        
        # YENİ: Günün Saati (Güneş Radyasyonu) Etkisi
        if time_of_day == "Afternoon" and precip == "Clear":
            ideal_clo -= 0.15  # Güneş tepede, insan daha sıcak hisseder, daha ince giyinmeli
        elif time_of_day == "Evening":
            ideal_clo += 0.15  # Güneş yok, ayaz var, daha kalın giyinmeli
        # Sabah (Morning) için nötr (güneş var ama hava henüz ısınmamış)
        
        if precip == "Rain":
            ideal_clo += 0.20
        elif precip == "Snow":
            ideal_clo += 0.40
            
        if profile == "Cold-natured":
            ideal_clo += 0.15 
        elif profile == "Hot-blooded":
            ideal_clo -= 0.15 
            
        if gender == "Female":
            ideal_clo += 0.10
            
        diff = total_clo - ideal_clo
        
        # --- ML EĞİTİM KURALLARI (Veriden Öğrenme) ---
        if diff < -0.3:
            sonuc = "Cold"
        elif diff > 0.3:
            sonuc = "Hot"
        else:
            if feels_like_c < 12:
                if top_clo < 0.5:
                    sonuc = "Cold (Top)"
                elif bottom_clo < 0.2:
                    sonuc = "Cold (Bottom)"
                else:
                    sonuc = "Comfortable"
            else:
                sonuc = "Comfortable"
                
        # 1. Rüzgar Öğrenimi: Rüzgar sertse (15+) ve üst inceyse (0.4 altı) kesinlikle üşür.
        if wind_kmh > 15 and top_clo < 0.4:
            sonuc = "Cold (Top)"
            
        # 2. Minimum Kalınlık Öğrenimi: Hava 20'den soğuksa aşırı ince (0.3 altı) giyilmez.
        if feels_like_c < 20:
            if top_clo < 0.3:
                sonuc = "Cold (Top)"
            if bottom_clo < 0.2:
                sonuc = "Cold (Bottom)"
                
        data.append([gender, profile, round(feels_like_c, 1), precip, round(wind_kmh, 1), time_of_day, top_clo, bottom_clo, sonuc])
        
    columns = ["Gender", "Profile", "Feels_Like_C", "Precipitation", "Wind_kmh", "Time_of_Day", "Top_CLO", "Bottom_CLO", "Outcome"]
    df = pd.DataFrame(data, columns=columns)
    
    file_path = os.path.join(os.path.dirname(__file__), "wardrobe_ai_dataset.csv")
    df.to_csv(file_path, index=False)
    print(f"Dataset Phase 2 generated successfully: {file_path}")

if __name__ == "__main__":
    generate_final_data(50000)
