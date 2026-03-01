import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import joblib
import os
import time

class GestureRecognizer:
    def __init__(self, main_page):
        # Hook to main page
        self.main_page = main_page
        self.last_gesture = None  
        self.current_candidate = None
        self.candidate_start_time = None
        self.confirmation_time = 0.5

        # MediaPipe hand detection setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Load trained gesture model
        model_path = "ML_Folder/gesture_model.pkl"
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = None
            print("No trained model found — running in landmark detection mode only.")

        # Column names used for the model
        self.columns = [f"{axis}{i}" for i in range(21) for axis in ["x", "y", "z"]]

        # For volume gesture
        self.max_volume_dist = None  # auto-calibrated max distance for 100% volume

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        gesture_label = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # Extract landmarks
                landmark_vector = []
                wrist = hand_landmarks.landmark[0]

                for lm in hand_landmarks.landmark:
                    landmark_vector.extend([
                        lm.x - wrist.x,
                        lm.y - wrist.y,
                        lm.z - wrist.z
                    ])

                landmark_vector = np.array(landmark_vector)

                # Predict gesture if model loaded
                if self.model:
                    df = pd.DataFrame([landmark_vector], columns=self.columns)
                    gesture_full_label = self.model.predict(df)[0]
                else:
                    gesture_full_label = "hand_detected"

                # Map dataset labels to actions
                if gesture_full_label in ["left_fist", "right_fist"]:
                    gesture_label = "fist"
                elif gesture_full_label in ["left_open", "right_open"]:
                    gesture_label = "open"
                elif gesture_full_label == "left_thumb":
                    gesture_label = "thumb_left"
                elif gesture_full_label == "right_thumb":
                    gesture_label = "thumb_right"
                elif gesture_full_label == "left_pinky":
                    gesture_label = "pinky_left"
                elif gesture_full_label == "right_pinky":
                    gesture_label = "pinky_right"
                elif gesture_full_label in ["left_volume", "right_volume"]:
                    gesture_label = "volume"
                else:
                    gesture_label = None

                now = time.time()

                if gesture_label is None:
                    self.current_candidate = None
                    self.candidate_start_time = None
                    return frame, None

                # If new candidate gesture detected
                if gesture_label != self.current_candidate:
                    self.current_candidate = gesture_label
                    self.candidate_start_time = now
                    return frame, None

                # If same gesture continues
                elapsed = now - self.candidate_start_time

                if elapsed >= self.confirmation_time:
                    # Only trigger if different from last confirmed gesture
                    if gesture_label != self.last_gesture:
                        print(f"Detected (confirmed): {gesture_label}")

                        # ---------------- Actions ----------------
                        if gesture_label == "fist":
                            self.main_page.start_playback()
                        elif gesture_label == "open":
                            self.main_page.pause_playback()
                        elif gesture_label == "thumb_left":
                            print("→ Loop toggled")
                            self.main_page.loop_value_changer()
                        elif gesture_label == "thumb_right":
                            print("→ Rewind / Previous triggered")
                            self.main_page.rewind_func()
                        elif gesture_label == "pinky_left":
                            print("→ Shuffle toggled")
                            self.main_page.shuffle_value_changer()
                        elif gesture_label == "pinky_right":
                            print("→ Next track triggered")
                            self.main_page.play_next_song()
                        elif gesture_label == "volume":
                            print("→ Volume control active")

                        # Mark as last confirmed
                        self.last_gesture = gesture_label

        else:
            # No hand detected
            if self.last_gesture:
                print("Lost hand")
                self.last_gesture = None

        # ---------------- Draw volume line and set volume if active ----------------
        if self.last_gesture == "volume" and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                h, w, _ = frame.shape
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]

                x1, y1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
                x2, y2 = int(index_tip.x * w), int(index_tip.y * h)

                # Euclidean distance
                dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                # Auto-calibrate max distance if first time
                if self.max_volume_dist is None:
                    self.max_volume_dist = dist if dist > 20 else 200  # fallback if too small

                # Map distance to 0-100%
                if dist <= self.max_volume_dist * 0.1:  # 10% threshold
                    volume_percent = 0
                else:
                    # Scale 11%-110% → 1-100%
                    scaled = (dist / self.max_volume_dist) * 100
                    scaled = min(scaled, 110)  # cap at 110
                    volume_percent = int(np.clip(scaled - 10, 1, 100))  # shift down by 10

                # Update volume in main page
                self.main_page.volume_bar.setValue(volume_percent)

                # Draw line from thumb tip to index fingertip
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

                # Draw circle at thumb tip and index fingertip
                cv2.circle(frame, (x1, y1), 6, (0, 255, 0), -1)
                cv2.circle(frame, (x2, y2), 6, (0, 255, 0), -1)

                # Midpoint above line for text
                mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2 - 15
                cv2.putText(frame, f"{volume_percent}% volume", (mid_x, mid_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        return frame, gesture_label
