import pandas as pd

DATA_FILE = "ML_Folder/gesture_data.csv"

data = pd.read_csv(DATA_FILE)

def reorder_label(label):
    # Special case: fix open_left / open_right
    if label == "fist_left":
        return "left_fist"
    if label == "fist_right":
        return "right_fist"
    if label == "open_left":
        return "left_open"
    if label == "open_right":
        return "right_open"
    
    parts = label.split("_")
    if len(parts) == 2:
        # current format: hand_gesture → gesture_hand
        hand, gesture = parts
        return f"{hand}_{gesture}"
    return label  # fallback for anything unexpected

data["label"] = data["label"].apply(reorder_label)

data.to_csv(DATA_FILE, index=False)

print("✅ Relabelled classes:", sorted(data["label"].unique()))
