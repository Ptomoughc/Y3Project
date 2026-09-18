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
        self.confirmation_time = 0.5  # 0.5s confirmation for all gestures
        self.gesture_cooldown = 0.3  # 0.3s cooldown after gesture is triggered
        self.last_trigger_time = 0  # Track when last gesture was triggered

        # Volume delay as gestures trigger immediately after
        self.volume_candidate_start = None
        self.volume_pending_percent = None
        self.volume_initial_delay = 0.5  # 0.5s before volume starts
        self.last_volume_update_time = 0
        self.volume_update_interval = 0.05  # 50ms between volume updates

        self.gesture_mappings = gesture_mappings or {}

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

    def update_gesture_mappings(self, new_mappings):
        self.gesture_mappings = {k.strip().lower(): v.strip().lower()
                                 for k, v in new_mappings.items()}

    def process_frame(self, frame, draw_landmarks=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        now = time.time()
        gesture_label = None
        triggered_action = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]

            if draw_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            # Feature vector
            landmark_vector = []
            wrist = hand_landmarks.landmark[0]
            for lm in hand_landmarks.landmark:
                landmark_vector.extend([lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z])
            landmark_vector = np.array(landmark_vector)

            # Predict gesture
            if self.model:
                df = pd.DataFrame([landmark_vector], columns=self.columns)
                gesture_full_label = self.model.predict(df)[0]
            else:
                gesture_full_label = "hand_detected"

            # Map to simple gestures
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


            # Handle volume gestures
            if gesture_label == "volume":
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                middle_tip = hand_landmarks.landmark[12]
                wrist = hand_landmarks.landmark[0]

                h, w, _ = frame.shape
                x1, y1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
                x2, y2 = int(index_tip.x * w), int(index_tip.y * h)
                mx, my = int(middle_tip.x * w), int(middle_tip.y * h)
                wx, wy = int(wrist.x * w), int(wrist.y * h)

                dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                hand_size = np.sqrt((mx - wx) ** 2 + (my - wy) ** 2)
                hand_size = max(hand_size, 1)

                normalized = dist / hand_size
                min_ratio, max_ratio = 0.35, 0.75
                scaled = (normalized - min_ratio) / (max_ratio - min_ratio)/3.5
                volume_percent = int(np.clip(scaled * 100, 0, 100))

                # Start volume after initial delay
                if self.volume_candidate_start is None:
                    self.volume_candidate_start = now
                    self.volume_pending_percent = volume_percent
                elif now - self.volume_candidate_start >= self.volume_initial_delay:
                    if now - self.last_volume_update_time >= self.volume_update_interval:
                        self.main_page.volume_bar.setValue(self.volume_pending_percent)
                        self.last_volume_update_time = now
                    self.volume_pending_percent = volume_percent
                else:
                    self.volume_pending_percent = volume_percent

                if draw_landmarks:
                    cv2.circle(frame, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
                    cv2.circle(frame, (x2, y2), 7, (255, 0, 255), cv2.FILLED)
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    cv2.putText(frame, f'{volume_percent} %', (cx - 40, cy - 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

                # Reset next possible tracking for non-volume gestures
                self.current_candidate = None
                self.candidate_start_time = None
                self.last_gesture = "volume"
                return frame, None  # Volume doesn't trigger a gesture action


            # Handle non-volume gestures with proper cooldown
            if gesture_label:
                # Check if we're in cooldown
                if now - self.last_trigger_time < self.gesture_cooldown:
                    # Don't trigger new gestures during cooldown
                    return frame, None
                
                # Check if this is a new candidate gesture
                if gesture_label != self.current_candidate:
                    self.current_candidate = gesture_label
                    self.candidate_start_time = now
                    return frame, None

                # Check if confirmation time has passed
                elapsed = now - self.candidate_start_time
                if elapsed >= self.confirmation_time:
                    # Only trigger if different from last triggered gesture to prevent repeated triggers
                    if gesture_label != self.last_gesture:
                        action = self.gesture_mappings.get(gesture_label)
                        if action:
                            if action == "play":
                                self.main_page.start_playback()
                                triggered_action = "play"
                            elif action == "pause":
                                self.main_page.pause_playback()
                                triggered_action = "pause"
                            elif action == "loop":
                                self.main_page.loop_value_changer()
                                triggered_action = "loop"
                            elif action == "rewind":
                                self.main_page.rewind_func()
                                triggered_action = "rewind"
                            elif action == "shuffle":
                                self.main_page.shuffle_value_changer()
                                triggered_action = "shuffle"
                            elif action == "skip":
                                self.main_page.play_next_song()
                                triggered_action = "skip"
                        
                        # Update last triggered time and gesture
                        self.last_trigger_time = now
                        self.last_gesture = gesture_label
                        
                        # Reset candidate to prevent immediate retrigger
                        self.current_candidate = None
                        self.candidate_start_time = None
                        
                        return frame, gesture_label
                    
                    # If same gesture as last, still update candidate time to prevent stuck state
                    if gesture_label == self.last_gesture:
                        self.candidate_start_time = now

        else:
            # No hand detected - reset tracking
            self.current_candidate = None
            self.candidate_start_time = None
            self.last_gesture = None
            self.volume_candidate_start = None

        return frame, triggered_action