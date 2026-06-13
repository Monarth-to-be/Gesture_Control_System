import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import requests
import time
import winsound # Added for audible lock/unlock feedback

# --- 1. MODEL CHECK ---
model_path = "hand_landmarker.task"

# --- 2. CONFIGURATION ---
ESP32_IP = "192.168.50.227" 
COOLDOWN_TIME = 1.0 

relay_states = {1: None, 2: None, 3: None, 4: None}
last_request_time = 0

# --- NEW: SYSTEM STATES ---
system_locked = True
gesture_state = "IDLE"  # Tracks the sliding motion: "START_OPENING" or "START_CLOSING"

def set_relay(relay_number, action):
    global last_request_time, relay_states
    
    if relay_states[relay_number] == action:
        return
        
    if time.time() - last_request_time < COOLDOWN_TIME:
        return
        
    try:
        url = f"http://{ESP32_IP}/cm?cmnd=Power{relay_number}%20{action}"
        requests.get(url, timeout=2)
        
        relay_states[relay_number] = action
        last_request_time = time.time()
        # Optional: Add a tiny beep here if you want audio feedback on relay clicks
        # winsound.Beep(2000, 50) 
    except requests.exceptions.RequestException:
        pass 

# Helper function to count the 4 main fingers (Index, Middle, Ring, Pinky)
# Note: We exclude the thumb from the calculation as its joint angles are 
# technically different and can cause false negatives. Holding up all your fingers 
# will reliably trigger this as an "open palm".
def count_main_fingers(hand_landmarks):
    count = 0
    tipIds = [8, 12, 16, 20]
    for tip_id in tipIds:
        if hand_landmarks[tip_id].y < hand_landmarks[tip_id - 2].y and hand_landmarks[tip_id].y < hand_landmarks[tip_id - 1].y:
            count += 1
    return count

# --- 3. INITIALIZE MEDIAPIPE ---
base_options = python.BaseOptions(model_asset_path=model_path)
# Changed num_hands to 2 so we can track both hands for the lock/unlock gesture
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    results = detector.detect(mp_image)

    if results.hand_landmarks and results.handedness:
        num_hands = len(results.hand_landmarks)

        # ---------------------------------------------------------
        # THE LOCK / UNLOCK GESTURE (Requires 2 Hands)
        # ---------------------------------------------------------
        if num_hands == 2:
            h1 = results.hand_landmarks[0]
            h2 = results.hand_landmarks[1]
            
            f1 = count_main_fingers(h1)
            f2 = count_main_fingers(h2)

            # If both palms are completely open (at least 8 main fingers detected)
            if f1 == 4 and f2 == 4:
                # Calculate horizontal distance between wrists (normalized 0.0 to 1.0)
                wrist_distance = abs(h1[0].x - h2[0].x)

                if system_locked:
                    # OPENING THE GATE (Unlock)
                    if wrist_distance < 0.2:  # Hands are close together
                        gesture_state = "START_OPENING"
                    elif wrist_distance > 0.45 and gesture_state == "START_OPENING": # Hands slid apart
                        system_locked = False
                        gesture_state = "IDLE"
                        # Ascending tone for UNLOCK
                        winsound.Beep(1000, 150)
                        winsound.Beep(1500, 150)
                        time.sleep(1) # Prevent double triggering

                else: 
                    # CLOSING THE DOOR (Lock)
                    if wrist_distance > 0.45: # Hands are far apart
                        gesture_state = "START_CLOSING"
                    elif wrist_distance < 0.2 and gesture_state == "START_CLOSING": # Hands slid together
                        system_locked = True
                        gesture_state = "IDLE"
                        # Descending tone for LOCK
                        winsound.Beep(1500, 150)
                        winsound.Beep(1000, 150)
                        time.sleep(1) # Prevent double triggering
            else:
                gesture_state = "IDLE" # Reset if fingers drop

        # ---------------------------------------------------------
        # RELAY CONTROL (Requires 1 Hand & Unlocked System)
        # ---------------------------------------------------------
        elif num_hands == 1 and not system_locked:
            hand_landmarks = results.hand_landmarks[0]
            model_handedness = results.handedness[0][0].category_name
            physical_hand = "Right" if model_handedness == "Left" else "Left"

            fingers_up = count_main_fingers(hand_landmarks)

            if 1 <= fingers_up <= 4:
                if physical_hand == "Right":
                    set_relay(fingers_up, "ON")
                elif physical_hand == "Left":
                    set_relay(fingers_up, "OFF")
    else:
        # Reset state if no hands are seen
        gesture_state = "IDLE"

cap.release()