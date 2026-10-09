import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

def train_model():
    print("1. Loading Phase 2 dataset...")
    file_path = os.path.join(os.path.dirname(__file__), "wardrobe_ai_dataset.csv")
    df = pd.read_csv(file_path)

    print("2. Encoding categorical variables (Including Time of Day)...")
    le_gender = LabelEncoder()
    le_profile = LabelEncoder()
    le_precip = LabelEncoder()
    le_time = LabelEncoder()
    le_outcome = LabelEncoder()

    df['Gender'] = le_gender.fit_transform(df['Gender'])
    df['Profile'] = le_profile.fit_transform(df['Profile'])
    df['Precipitation'] = le_precip.fit_transform(df['Precipitation'])
    df['Time_of_Day'] = le_time.fit_transform(df['Time_of_Day'])
    df['Outcome'] = le_outcome.fit_transform(df['Outcome'])

    print("3. Splitting Train/Test data (80% Train, 20% Test)...")
    X = df[['Gender', 'Profile', 'Feels_Like_C', 'Precipitation', 'Wind_kmh', 'Time_of_Day', 'Top_CLO', 'Bottom_CLO']]
    y = df['Outcome']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("4. Training Random Forest Algorithm (Phase 2)...")
    # GitHub 25MB sınırına takılmamak için modeli "Pruning" (Budama) yöntemiyle optimize ediyoruz.
    rf_model = RandomForestClassifier(n_estimators=45, max_depth=16, min_samples_leaf=2, random_state=42)
    rf_model.fit(X_train, y_train)

    print("5. Testing Model...")
    y_pred = rf_model.predict(X_test)
    print(f"\n--- MODEL ACCURACY ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le_outcome.classes_))

    print("\n6. Saving Trained Model and Encoders...")
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wardrobe_model.pkl")
    
    encoders = {
        'gender': le_gender,
        'profile': le_profile,
        'precip': le_precip,
        'time': le_time,
        'outcome': le_outcome
    }
    
    joblib.dump({'model': rf_model, 'encoders': encoders}, model_path)
    print(f"✅ Success! Phase 2 Model saved as '{model_path}'.")

if __name__ == "__main__":
    train_model()
