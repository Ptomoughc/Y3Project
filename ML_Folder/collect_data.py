import cv2
import mediapipe as mp
import numpy as np
import csv
import os

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

DATA_FILE = "ML_Folder/gesture_data.csv"

# Counters
counts = {
    "fist_left":0, "fist_right":0,
    "open_left":0, "open_right":0,
    "thumb_left":0, "thumb_right":0,
    "pinky_left":0, "pinky_right":0,
    "volume_left":0, "volume_right":0
}

# Create CSV file with header if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        header = []
        for i in range(21):
            header += [f"x{i}", f"y{i}", f"z{i}"]
        header += ["label"]
        writer.writerow(header)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

print("Press:")
print(" O → record OPEN")
print(" F → record FIST")
print(" T → record THUMB gesture")
print(" P → record PINKY gesture")
print(" V → record VOLUME pinch gesture")
print(" Q → quit")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                               results.multi_handedness):

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            hand_label = handedness.classification[0].label.lower()  # get left or right label

            wrist = hand_landmarks.landmark[0]

            landmark_vector = []
            for lm in hand_landmarks.landmark:
                # Normalize relative to wrist
                landmark_vector.extend([
                    lm.x - wrist.x,
                    lm.y - wrist.y,
                    lm.z - wrist.z
                ])

            landmark_vector = np.array(landmark_vector)

            key = cv2.waitKey(1) & 0xFF

            label = None
            if key == ord('o'):
                label = f"open_{hand_label}"
            elif key == ord('f'):
                label = f"fist_{hand_label}"
            elif key == ord('t'):
                label = f"thumb_{hand_label}"
            elif key == ord('p'):
                label = f"pinky_{hand_label}"
            elif key == ord('v'):
                label = f"volume_{hand_label}"
            elif key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                exit()

            # Save if a valid label key pressed
            if label is not None:
                with open(DATA_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(list(landmark_vector) + [label])

                counts[label] += 1
                print(f"Saved {label} | Count: {counts[label]}")

    cv2.imshow("Collect Gesture Data", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
