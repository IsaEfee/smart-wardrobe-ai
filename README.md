# 🌦️ Smart AI Wardrobe Assistant (Hybrid Architecture)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-brightgreen.svg)
![Bilingual](https://img.shields.io/badge/Language-English%20%7C%20Turkish-orange.svg)
![Database](https://img.shields.io/badge/Database-JSON-lightgrey.svg)

An intelligent, machine-learning-powered web application that recommends the perfect daily outfit based on live weather data, scientific thermal insulation (CLO) values, your personal thermal profile, and a multi-tag fashion rule engine.

## 🚀 Live Demo
*(Paste your Streamlit Cloud link here once deployed, e.g., https://smart-wardrobe-ai.streamlit.app)*

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

- **Frontend/UI**: Streamlit
- **Machine Learning**: Scikit-Learn (Random Forest)
- **Data Processing**: Pandas, NumPy
- **External API**: OpenWeatherMap REST API (Live & 5-Day Forecast)
- **Database**: Native JSON Document

## 💻 Local Installation

If you want to run this project on your local machine:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-wardrobe-ai.git
cd smart-wardrobe-ai
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit application:
```bash
streamlit run app.py
```

## 📚 Academic Context
This project demonstrates the integration of traditional Machine Learning algorithms with real-world deterministic rule engines. It successfully tackles the "cold start", "fashion mismatch", and "probabilistic hallucination" problems inherent in pure AI recommenders by applying strict architectural Separation of Concerns.
