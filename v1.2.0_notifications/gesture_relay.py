import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import requests
import time
import winsound
from winotify import Notification # Modern, stable Windows notification library

# --- 1. MODEL CHECK ---
model_path = "hand_landmarker.task"

# --- 2. CONFIGURATION ---
ESP32_IP = "192.168.50.227" 
COOLDOWN_TIME = 1.0 

relay_states = {1: None, 2: None, 3: None}
last_request_time = 0

# --- SYSTEM STATES ---
system_locked = True
gesture_state = "IDLE" 
lock_cooldown_until = 0 

def set_relay(relay_number, action):
    global last_request_time, relay_states
    
    if relay_number not in relay_states:
        return
        
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
        pass 

def count_main_fingers(hand_landmarks):
    count = 0
    tipIds = [8, 12, 16, 20]
    for tip_id in tipIds:
        if hand_landmarks[tip_id].y < hand_landmarks[tip_id - 2].y and hand_landmarks[tip_id].y < hand_landmarks[tip_id - 1].y:
            count += 1
    return count

# --- 3. INITIALIZE MEDIAPIPE ---
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    results = detector.detect(mp_image)

    current_time = time.time()
    num_hands = len(results.hand_landmarks) if results.hand_landmarks else 0

    # ---------------------------------------------------------
    # THE LOCK / UNLOCK GESTURE (Requires 2 Hands)
    # ---------------------------------------------------------
    if num_hands == 2:
        h1 = results.hand_landmarks[0]
        h2 = results.hand_landmarks[1]
        
        f1 = count_main_fingers(h1)
        f2 = count_main_fingers(h2)

        wrist_distance = abs(h1[0].x - h2[0].x)

        if f1 >= 2 and f2 >= 2:
            if current_time > lock_cooldown_until:
                if system_locked:
                    # OPENING THE GATE (Unlock)
                    if wrist_distance < 0.3: 
                        gesture_state = "START_OPENING"
                    elif wrist_distance > 0.45 and gesture_state == "START_OPENING":
                        system_locked = False
                        gesture_state = "IDLE"
                        lock_cooldown_until = current_time + 2.0
                        
                        # Winotify Unlock Notification
                        toast = Notification(app_id="Gesture Relay", title="🔓 System Unlocked", msg="Gesture control active.", duration="short")
                        toast.show()
                        
                        winsound.Beep(1000, 150)
                        winsound.Beep(1500, 150)
                else: 
                    # CLOSING THE DOOR (Lock)
                    if wrist_distance > 0.45: 
                        gesture_state = "START_CLOSING"
                    elif wrist_distance < 0.3 and gesture_state == "START_CLOSING":
                        system_locked = True
                        gesture_state = "IDLE"
                        lock_cooldown_until = current_time + 2.0
                        
                        # Winotify Lock Notification
                        toast = Notification(app_id="Gesture Relay", title="🔒 System Locked", msg="Gesture control paused.", duration="short")
                        toast.show()
                        
                        winsound.Beep(1500, 150)
                        winsound.Beep(1000, 150)
        else:
            if f1 == 0 and f2 == 0:
                gesture_state = "IDLE"

    # ---------------------------------------------------------
    # RELAY CONTROL (Requires 1 Hand, Unlocked System, Passed Grace Period)
    # ---------------------------------------------------------
    elif num_hands == 1 and not system_locked and current_time > lock_cooldown_until:
        hand_landmarks = results.hand_landmarks[0]
        model_handedness = results.handedness[0][0].category_name
        physical_hand = "Right" if model_handedness == "Left" else "Left"

        fingers_up = count_main_fingers(hand_landmarks)

        if 1 <= fingers_up <= 3:
            if physical_hand == "Right":
                set_relay(fingers_up, "ON")
            elif physical_hand == "Left":
                set_relay(fingers_up, "OFF")
    
    elif num_hands == 0:
        gesture_state = "IDLE"

cap.release()