# File is used to rename gesture names


import pandas as pd

DATA_FILE = "ML_Folder/gesture_data.csv"

data = pd.read_csv(DATA_FILE)

def reorder_label(label):
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
        # current format: hand_gesture to gesture_hand
        hand, gesture = parts
        return f"{hand}_{gesture}"
    return label  # Do nothing it it fails

data["label"] = data["label"].apply(reorder_label)

data.to_csv(DATA_FILE, index=False)

print("Relabelled classes:", sorted(data["label"].unique()))
