import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

DATA_FILE = "ML_Folder/gesture_data.csv"
MODEL_FILE = "ML_Folder/gesture_model.pkl"

# Load dataset
data = pd.read_csv(DATA_FILE)

# ---------------------------
# Sanity check label set
# ---------------------------
expected_labels = {
    "left_fist", "left_open", "left_pinky", "left_thumb", "left_volume",
    "right_fist", "right_open", "right_pinky", "right_thumb", "right_volume"
}

found_labels = set(data["label"].unique())

print("Labels found in dataset:", sorted(found_labels))

missing = expected_labels - found_labels
extra = found_labels - expected_labels

if missing:
    print("⚠️ Missing labels:", missing)
if extra:
    print("⚠️ Unexpected labels:", extra)

# ---------------------------
# Features and labels
# ---------------------------
X = data.drop(columns=["label"])
y = data["label"]

# Show class balance
print("\nSamples per class:")
print(y.value_counts())

# ---------------------------
# Train / test split
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

# ---------------------------
# Model
# ---------------------------
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# ---------------------------
# Evaluate
# ---------------------------
y_pred = model.predict(X_test)

print("\n=== Test Accuracy ===")
print(accuracy_score(y_test, y_pred))

print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred, zero_division=0))

# ---------------------------
# Save model
# ---------------------------
joblib.dump(model, MODEL_FILE)
print(f"\n✅ Model saved to: {MODEL_FILE}")
