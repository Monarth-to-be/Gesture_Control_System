# v1.0.0 — Baseline: Single-Hand Relay Control

I'm controlling the ESP32 through gesture, where I've flashed the ESP32 with Tasmota firmware & connected the ESP32 with 4 relays to control lights & speaker in my room. The script runs invisibly at Windows login via file "Start_Gesture_Relay.vbs"

# What This Version Does
- Reads webcam feed via OpenCV, detects hands with MediaPipe HandLandmarker
- Counts extended fingers (index, middle, ring, pinky — thumb excluded)
- **Right hand (1–4 fingers)** → Turns ON relays 1–4
- **Left hand (1–4 fingers)** → Turns OFF relays 1–4
- Runs invisibly at Windows login via `Start_Gesture_Relay.vbs`

# Must haves

- Python: Latest verison
- Windows 10 or later
- Webcam
- ESP32 flashed with Tasmota firmware
- ESP32 connected with 4 relays | Or you can modify file as per your need

# Dependencies (Run it in powershell)

pip install mediapipe opencv-python requests

Also requires: `hand_landmarker.task` model file (MediaPipe Models) | paste it in same folder where you put your Python file.

# Files in This Version


- `gesture_relay.py` | Main script — place this in same folder as C:/Users/monar (your local PC)/Gestures/v1.0.0_baseline |
- `hand_landmarker.task` | MediaPipe Models |
- `Start_Gesture_Relay.vbs` | Windows startup launcher (uses pythonw.exe) |


# Configuration
Edit line in `gesture_relay.py`:
```python
ESP32_IP = "192.168.50.227"   # ← Your ESP32's local IP
```

# Known Limitation (Will be Fixed in v1.1.0)
- No lock/unlock mechanism.** Any fingers visible = relay commands sent.  
- You must physically cover the camera shutter when working at desk, or else it will trigger your relays anytime it sees your fingers.

# How to Run (for testing)
1.open powershell
2.Go to directory where your python file is | for this example cd "C:\Users\monar\Gestures\v1.0.0_baseline" 
3.then type command `python gesture_relay.py`

# How to Run (production — invisible)
Double-click `Start_Gesture_Relay.vbs`  
OR: Manually Place `Start_Gesture_Relay.vbs` in `shell:startup` folder for auto-start at login.


