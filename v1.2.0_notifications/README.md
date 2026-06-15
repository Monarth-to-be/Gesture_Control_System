# v1.2.0 — Buffer Fix, Toast Notifications, & Relaxed Gestures

I'm controlling the ESP32 through gestures, where I've flashed the ESP32 with Tasmota firmware. It is connected to relays to control devices in my room. The script runs invisibly in the background.

### What This Version Does
* **Everything from v1.1.0**, plus major bug fixes and improvements.
* **Camera Lag Fixed:** The camera no longer stores old frames, meaning gestures are now read instantly without delays or accidental misfires.
* **Windows Notifications:** You will now see a visual popup (toast notification) on your screen when you lock or unlock the system.
* **Easier Locking/Unlocking:** You don't have to hold your hands perfectly flat anymore. The system now forgives slightly bent pinky or ring fingers while you slide your hands to lock/unlock.
* **Removed Relay 4:** The script only controls Relays 1 to 3 now. Showing 1, 2, or 3 fingers turns the corresponding relay ON (right hand) or OFF (left hand).
* Runs invisibly at Windows login via `Start_Gesture_Relay.vbs`.

### Must haves
* Python: Latest version
* Windows 10 or later
* Webcam
* ESP32 flashed with Tasmota firmware
* ESP32 connected with 3 relays (you can modify the code if you need more).

### Dependencies (Run it in powershell)
```powershell
pip install mediapipe opencv-python requests winotify
```
*(Note: `winsound` is used for audio feedback but it is a Python standard library, so no install is needed)*

Also requires the `hand_landmarker.task` model file (MediaPipe Models). Paste it in the same folder where you put your Python file. 

### Files in This Version
* `gesture_relay.py` | Main script — place this in the same folder as this README. |
* `hand_landmarker.task` | MediaPipe Models |
* `Start_Gesture_Relay.vbs` | Windows startup launcher (runs invisibly) |

### Configuration
Edit lines in `gesture_relay.py`:
```python
ESP32_IP = "192.168.50.227"   # ← Your ESP32's local IP
```

### Major Bugs Fixed in This Version
* **The "Camera Buffer" Bug:** Previously, the camera would queue up old frames while the system was pausing. This caused the relays to misfire because the camera saw old, transitional finger movements. We fixed this by forcing the camera to only use the very latest frame!
* **The "Double Trigger" Bug:** We removed `time.sleep()` completely. The system now uses a smarter "time gate" of 2.0 seconds that doesn't freeze the camera, preventing accidental lock/unlock spamming.

### How to Run (for testing)
1. Open PowerShell
2. Go to the directory where your python file is (e.g. `cd "C:\Users\monar\Downloads\Gestures\v1.2.0_notifications"`)
3. Run the command: `python gesture_relay.py`

### How to Run (production — invisible)
Double-click `Start_Gesture_Relay.vbs`.
OR: To start it automatically when you log in, place `Start_Gesture_Relay.vbs` inside your `shell:startup` folder (Press Win + R, type `shell:startup`, and hit Enter).
