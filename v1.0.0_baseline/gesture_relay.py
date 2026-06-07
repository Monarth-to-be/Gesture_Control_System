import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import requests
import time
import os

# --- 1. MODEL CHECK ---
model_path = "hand_landmarker.task"

# --- 2. CONFIGURATION ---
ESP32_IP = "192.168.50.227" 
COOLDOWN_TIME = 1.0 

relay_states = {1: None, 2: None, 3: None, 4: None}
last_request_time = 0

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
    except requests.exceptions.RequestException:
        pass # Silently ignore network errors so the script doesn't crash

# --- 3. INITIALIZE MEDIAPIPE ---
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
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

    fingers_up = 0

    if results.hand_landmarks and results.handedness:
        hand_landmarks = results.hand_landmarks[0]
        model_handedness = results.handedness[0][0].category_name
        physical_hand = "Right" if model_handedness == "Left" else "Left"

        tipIds = [8, 12, 16, 20]
        for tip_id in tipIds:
            if hand_landmarks[tip_id].y < hand_landmarks[tip_id - 2].y and hand_landmarks[tip_id].y < hand_landmarks[tip_id - 1].y:
                fingers_up += 1

        if 1 <= fingers_up <= 4:
            if physical_hand == "Right":
                set_relay(fingers_up, "ON")
            elif physical_hand == "Left":
                set_relay(fingers_up, "OFF")

cap.release()