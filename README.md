# 🌦️ Smart AI Wardrobe Assistant (Hybrid Architecture)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-brightgreen.svg)
![Bilingual](https://img.shields.io/badge/Language-English%20%7C%20Turkish-orange.svg)
![Database](https://img.shields.io/badge/Database-JSON-lightgrey.svg)

An intelligent, machine-learning-powered web application that recommends the perfect daily outfit based on live weather data, scientific thermal insulation (CLO) values, your personal thermal profile, and a multi-tag fashion rule engine.

## 🚀 Live Demo
👉 **[https://smart-wardrobe-ai-isa.streamlit.app/](https://smart-wardrobe-ai-isa.streamlit.app/)**

## 🧠 The Hybrid Architecture (How It Works)

This project solves real-world recommender system challenges by combining a **Probabilistic Machine Learning Model** with a strict **Deterministic Rule & Style Engine**:

1. **Thermodynamic AI (The ML Core)**: A Random Forest Classifier trained on **50,000 synthetically generated** (but biologically accurate) data points. The model is highly optimized via **Tree Pruning** (`max_depth=16`, `n_estimators=45`) to achieve **95.04% accuracy** while maintaining a compact size (< 25MB). It calculates the exact CLO (Clothing Insulation) target required to keep a human comfortable based on real-time weather and their metabolic profile.
2. **Multi-Tag Fashion Engine**: Clothes are not just numbers; they have styles. The system uses a **Mathematical Set Intersection Algorithm** to ensure fashion compatibility. (e.g., A top with `["Sport", "Casual"]` will intersect with a bottom having `["Casual", "Smart-Casual"]` to form a `Casual` outfit, mathematically preventing absurd combinations like Sweatpants + Blazers).
3. **Smart Layering (3-Layer Simulation)**: Introduces dynamic UI add-ons (like an "Undershirt" checkbox). The engine intelligently deducts base-layer insulation from the AI's target *before* searching the wardrobe, seamlessly simulating a 3-layer system without exponential time complexity (O(N³)).
4. **Context-Aware Rule Engine**: Implements strict guardrails (e.g., Scarves and Beanies auto-added below 10°C, Gloves below 5°C, Sunglasses for clear mornings, and forbidding shorts in cold/rain).

## ✨ Key Features

- **📅 5-Day Weekly Planner**: Fetches 3-hour interval data from OpenWeatherMap, allowing users to generate a 5-day wardrobe plan specifically for their preferred time of day (Morning, Afternoon, or Evening).
- **🗄️ JSON Database (Separation of Concerns)**: The wardrobe items and style tags are fully decoupled into `wardrobe_db.json`, ensuring the AI logic scales independently from the clothing inventory.
- **🌍 Bilingual Interface**: Fully supports English and Turkish seamlessly on the fly.
- **🚪 Personalized Wardrobe**: Users select their owned items, and the AI strictly filters predictions to match their inventory.

## 🛠️ Tech Stack

- **Mobile & Web Backend**: FastAPI, Uvicorn, SQLite
- **Web Demo / UI**: Streamlit
- **Machine Learning**: Scikit-Learn (Random Forest, Pruned)
- **Data Processing**: Pandas, NumPy
- **External API**: OpenWeatherMap REST API (Live & 5-Day Forecast)
- **Database**: SQLite (User profiles, Persistent wardrobe & Feedback history), Native JSON (Clothing catalog)

## 📁 Repository Structure

```text
├── backend/
│   ├── api.py               # FastAPI REST API endpoints
│   ├── database.py          # SQLite User profiles & online feedback learning
│   ├── engine.py            # Recommender core, thermodynamic rules & weather
│   └── wardrobe_app.db      # Local SQLite database (auto-generated, git-ignored)
├── data/
│   ├── wardrobe_db.json     # Multi-tag Clothing Attributes & CLO values
│   └── wardrobe_ai_dataset.csv # 50,000 biological training samples
├── models/
│   └── wardrobe_model.pkl   # Pre-trained pruned Random Forest model (< 22MB)
├── scripts/
│   ├── data_generator.py    # Synthetic dataset generator (50k biological records)
│   └── model_training.py    # Random Forest training with max-depth pruning
├── app.py                   # Streamlit live web interactive dashboard
├── run_api.py               # One-click runner for FastAPI backend server
├── requirements.txt         # Project Python dependencies
└── README.md
```

## 💻 Running the Project

### 1. Run the Backend API (For Mobile App Integration)
```bash
python run_api.py
```
* Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### 2. Run the Streamlit Web Showcase
```bash
streamlit run app.py
```

## 📚 Academic Context
This project demonstrates the integration of traditional Machine Learning algorithms with real-world deterministic rule engines and a **Human-in-the-Loop Adaptive Online Learning** loop. It successfully tackles the "cold start", "fashion mismatch", and "probabilistic hallucination" problems inherent in pure AI recommenders by applying strict architectural Separation of Concerns.
