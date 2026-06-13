# v1.1.0 — Lock/Unlock Sliding Gate Gesture + Audio Feedback

I'm controlling the ESP32 through gesture, where I've flashed the ESP32 with Tasmota firmware & connected the ESP32 with 4 relays to control lights & speaker in my room. The script runs invisibly at Windows login via file "Start_Gesture_Relay.vbs"

### What This Version Does
* Reads webcam feed via OpenCV, detects hands with MediaPipe HandLandmarker (upgraded to track 2 hands)
* Added **lock/unlock state machine** — relays only trigger when system is unlocked
* **Unlock gesture:** Both hands open (palms facing camera), start close together, slide apart. Ascending beep (1000→1500 Hz) indicates unlock
* **Lock gesture:** Both hands open, start far apart, slide together. Descending beep (1500→1000 Hz) indicates lock
* Counts extended fingers (index, middle, ring, pinky — thumb excluded)
* Right hand (1–4 fingers) → Turns ON relays 1–4
* Left hand (1–4 fingers) → Turns OFF relays 1–4
* Runs invisibly at Windows login via Start_Gesture_Relay.vbs

### Must haves
* Python: Latest version
* Windows 10 or later
* Webcam
* ESP32 flashed with Tasmota firmware
* ESP32 connected with 4 relays | Or you can modify file as per your need

### Dependencies (Run it in powershell)
```powershell
pip install mediapipe opencv-python requests
```
Also requires: `hand_landmarker.task` model file (MediaPipe Models) | paste it in same folder where you put your Python file. 
*(Note: `winsound` is used for audio feedback but it is a Python standard library, so no install is needed)*

### Files in This Version
* `gesture_relay.py` | Main script — place this in same folder as `C:/Users/monar/Gestures/v1.1.0_lock_unlock_gesture` |
* `hand_landmarker.task` | MediaPipe Models |
* `Start_Gesture_Relay.vbs` | Windows startup launcher (uses pythonw.exe) |

### Configuration
Edit lines in `gesture_relay.py`:
```python
ESP32_IP = "192.168.50.227"   # ← Your ESP32's local IP
```
Lock/Unlock Thresholds (can be calibrated as per need):
```python
CLOSE_THRESHOLD = 0.2   # wrist distance to start unlock (hands near)
OPEN_THRESHOLD  = 0.45  # wrist distance to complete unlock (hands far)
```

### Known Limitation (Will be Fixed in v1.2.0)
* `time.sleep(1)` was used after lock/unlock transitions to prevent double-triggering. This caused **relay misfires** because the webcam driver kept buffering frames during `sleep()`. On wake-up, Python processed queued frames showing transitional finger positions which triggered relay 1, 2, or 3 before hands were fully lowered.
* Relay 4 still present (will be removed in v1.2.0) | That's a personal reason but user can keep it if needed.

### How to Run (for testing)
1. Open powershell
2. Go to directory where your python file is | for this example `cd "C:\Users\monar\Gestures\v1.1.0_lock_unlock_gesture"`
3. Then type command `python gesture_relay.py`

### How to Run (production — invisible)
Double-click `Start_Gesture_Relay.vbs`
OR: Manually Place `Start_Gesture_Relay.vbs` in `shell:startup` folder for auto-start at login.
