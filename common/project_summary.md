# Gesture Control System

## Project Overview
This project is a computer vision-based gesture control system designed to control smart home devices (specifically, ESP32 modules with relays) using hand gestures. It leverages a webcam feed, OpenCV for image processing, and MediaPipe's HandLandmarker for accurate hand and finger detection.

## Key Features
- **Gesture-Based Relay Control:** Detects the number of extended fingers to trigger specific relays (e.g., turning lights or speakers on/off).
- **Lock/Unlock Mechanism:** Includes a sliding gate gesture to lock and unlock the system, preventing accidental triggers when the user is simply moving their hands in front of the camera.
- **Audio Feedback:** Provides audible cues (ascending/descending beeps) to indicate when the system has been locked or unlocked.
- **Invisible Execution:** Designed to run silently in the background upon Windows login using a VBScript launcher.

## Technology Stack
- Python
- OpenCV
- MediaPipe
- ESP32 (flashed with Tasmota firmware)
- Windows (for the VBScript background launcher)

<!-- Repository maintenance update: Basic commit test -->
