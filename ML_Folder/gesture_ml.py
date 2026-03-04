import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import joblib
import os
import time


class GestureRecognizer:
    def __init__(self, main_page, gesture_mappings):
        self.main_page = main_page
        self.last_gesture = None
        self.current_candidate = None
        self.candidate_start_time = None
        self.confirmation_time = 0.5

        # Gesture to action dictionary (excludes volume as we do not want that to be changed)
        self.gesture_mappings = gesture_mappings or {}

        print(self.gesture_mappings)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.mp_draw = mp.solutions.drawing_utils

        model_path = "ML_Folder/gesture_model.pkl"
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = None
            print("No trained model found.")

        self.columns = [f"{axis}{i}" for i in range(21) for axis in ["x", "y", "z"]]
        self.max_volume_dist = None

    def update_gesture_mappings(self, new_mappings):
        self.gesture_mappings = {
            k.strip().lower(): v.strip().lower()
            for k, v in new_mappings.items()
        }

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        gesture_label = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                landmark_vector = []
                wrist = hand_landmarks.landmark[0]

                for lm in hand_landmarks.landmark:
                    landmark_vector.extend([
                        lm.x - wrist.x,
                        lm.y - wrist.y,
                        lm.z - wrist.z
                    ])

                landmark_vector = np.array(landmark_vector)

                if self.model:
                    df = pd.DataFrame([landmark_vector], columns=self.columns)
                    gesture_full_label = self.model.predict(df)[0]
                else:
                    gesture_full_label = "hand_detected"

                # Group features up
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

                # New possible gesture
                if gesture_label != self.current_candidate:
                    self.current_candidate = gesture_label
                    self.candidate_start_time = now
                    return frame, None

                # Confirm gesture
                elapsed = now - self.candidate_start_time

                if elapsed >= self.confirmation_time:
                    if gesture_label != self.last_gesture:

                        print(f"\nDetected (confirmed): {gesture_label}")

                        # Volume checker
                        if gesture_label == "volume":
                            print("Volume mode activated")
                            self.last_gesture = "volume"
                            self.max_volume_dist = None
                            break

                        # All other gestures in dictionary
                        action = self.gesture_mappings.get(gesture_label)

                        if action:
                            print(f"Instruction to execute: {action}")

                            if action == "play":
                                self.main_page.start_playback()

                            elif action == "pause":
                                self.main_page.pause_playback()

                            elif action == "loop":
                                self.main_page.loop_value_changer()

                            elif action == "rewind":
                                self.main_page.rewind_func()

                            elif action == "shuffle":
                                self.main_page.shuffle_value_changer()

                            elif action == "skip":
                                self.main_page.play_next_song()

                        else:
                            print("No instruction mapped to this gesture.")

                        self.last_gesture = gesture_label

        else:
            if self.last_gesture:
                print("Lost hand")
                self.last_gesture = None

        if self.last_gesture == "volume" and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                h, w, _ = frame.shape
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]

                x1, y1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
                x2, y2 = int(index_tip.x * w), int(index_tip.y * h)

                dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                if self.max_volume_dist is None:
                    self.max_volume_dist = dist if dist > 20 else 200

                scaled = min((dist / self.max_volume_dist) * 100, 110)
                volume_percent = int(np.clip(scaled - 10, 0, 100))

                self.main_page.volume_bar.setValue(volume_percent)

                # Draw circles on fingertips
                cv2.circle(frame, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (x2, y2), 5, (255, 0, 255), cv2.FILLED)

                # Draw line between fingers
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                # Center point
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                cv2.circle(frame, (cx, cy), 0, (0, 255, 255), cv2.FILLED)

                # Display volume percentage above hand
                cv2.putText(
                    frame,
                    f'{volume_percent} %',
                    (cx - 40, cy - 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    3
                )

        return frame, gesture_label