import pandas as pd

DATA_FILE = "ML_Folder/gesture_data.csv"

# Load CSV
data = pd.read_csv(DATA_FILE)

# Get unique labels
unique_labels = sorted(data["label"].unique())

print("Unique gesture labels:")
for label in unique_labels:
    print(label)
