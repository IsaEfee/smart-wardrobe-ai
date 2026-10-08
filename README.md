# 🌦️ Smart AI Wardrobe Assistant

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-brightgreen.svg)
![Bilingual](https://img.shields.io/badge/Language-English%20%7C%20Turkish-orange.svg)

An intelligent, machine-learning-powered web application that recommends the perfect daily outfit based on live weather data, scientific thermal insulation (CLO) values, and your personal thermal profile.

## 🚀 Live Demo
*(You can paste your Streamlit Cloud link here once deployed, e.g., https://smart-wardrobe-ai.streamlit.app)*

## 🧠 How It Works

This project goes beyond simple "if-else" weather apps by combining a **Machine Learning Classification Model** with a strict **Rule-Based Filtering Engine**:

1. **Live Weather Data**: Fetches real-time temperature, precipitation, and wind speed using the OpenWeatherMap API.
2. **Scientific Thermal Standards**: Utilizes ASHRAE 55 CLO (Clothing Insulation) indices to calculate the mathematical insulation target required to keep a human comfortable outdoors.
3. **Machine Learning Core**: A Random Forest Classifier trained on 5,000 synthetically generated (but biologically accurate) data points. The model predicts thermal comfort ("Comfortable", "Hot", "Cold") based on the user's gender, thermal profile (Hot-blooded/Cold-natured), weather conditions, and clothing CLO combinations.
4. **Rule Engine**: Filters the ML targets against the user's actual virtual wardrobe, enforcing logical fashion and anatomical guardrails (e.g., forbidding shorts below 20°C, requiring hoods in rain).

## ✨ Features

- **Bilingual Interface**: Fully supports both English and Turkish UIs seamlessly.
- **Personalized Wardrobe**: Users can select exactly which items they own, and the AI will only recommend combinations using those specific items.
- **Dynamic Onboarding**: Asks for gender and thermal profile to tailor the ML predictions specifically for the user's body type.
- **Presentation Mode**: Allows users to manually override live weather data to test edge cases (e.g., Snowing at -5°C vs Sunny at 30°C) during presentations.

## 🛠️ Tech Stack

- **Frontend/UI**: Streamlit
- **Machine Learning**: Scikit-Learn (Random Forest)
- **Data Processing**: Pandas, NumPy
- **External API**: OpenWeatherMap REST API

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
This project was developed to demonstrate the integration of traditional Machine Learning algorithms with real-world deterministic rule engines, specifically solving the "cold start" and "context-awareness" problems in recommender systems.
