# EYE-BOT-CODE
Code for my IOT Project


# Raspberry Pi Eye-Tracking Drowsiness Detection System

This project uses a Raspberry Pi with a camera module to detect eye blinks and track drowsiness or tiredness. When abnormal blinking patterns are detected, alerts are sent via Twilio SMS and logged into Firebase.

---

## 📦 Features

- Real-time face and eye tracking using `dlib` and `OpenCV`
- Dynamic blink rate analysis to detect **drowsiness** and **tiredness**
- Alerts via SMS using **Twilio**
- Logs alert data to **Firebase Firestore**
- Designed for IoT use and fatigue monitoring

---

## 🧰 Requirements

Install the following dependencies:

```bash
sudo apt update
sudo apt install libatlas-base-dev libjasper-dev libqtgui4 python3-pyqt5 libqt4-test
pip3 install opencv-python opencv-python-headless
pip3 install dlib
pip3 install picamera2
pip3 install firebase-admin
pip3 install twilio


🛠️ Setup Instructions
1. Firebase Setup:
Go to Firebase Console.

Create a new project.

Navigate to Project Settings > Service accounts.

Click Generate new private key to download the .json file.

Rename it (e.g., firebase-adminsdk.json) and place it in your project folder.

2. Twilio Setup:
Create a Twilio account.

Verify your phone number.

Navigate to Console Dashboard to get:

Account SID

Auth Token

Twilio Phone Number

✏️ What to Replace in the Code
Open your Python script and replace the following placeholders:

1. Firebase Credential File Path:
Replace:
cred = credentials.Certificate("path/to/your/firebase-adminsdk.json")
With:
cred = credentials.Certificate("firebase-adminsdk.json")

2. Twilio Configuration:
Replace the following lines with your actual Twilio account details:
account_sid = "REPLACE_WITH_TWILIO_ACCOUNT_SID"
auth_token = "REPLACE_WITH_TWILIO_AUTH_TOKEN"
from_ = "+REPLACE_WITH_TWILIO_PHONE_NUMBER"
to = "+REPLACE_WITH_RECEIVER_PHONE_NUMBER"

Example:
account_sid = "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
auth_token = "your_auth_token_here"
from_ = "+1234567890"
to = "+16395551234"

▶️ Step 3: Run the Code
Once everything is set up, run your Python script using:
python3 your_script_name.py
Make sure your Raspberry Pi Camera Module is connected and enabled. The system will:

Start a live video feed using the camera

Use facial landmarks to detect eye blinks

Count blinks per minute to determine drowsiness or tiredness

Send an SMS alert using Twilio when a threshold is passed

Store alert data in Firebase

✅ Final Notes
Ensure the lighting conditions are good so the camera can accurately detect facial features.

Double-check all credential paths and environment configurations.

You can tweak blink rate thresholds in the code based on your observations.

💡 Prototype Status
This is a prototype-level project designed for academic and IoT development purposes. Use it as a foundation and expand with more advanced features such as cloud dashboards, audio alerts, or better model integration (e.g., with mediapipe or custom-trained ML models).

📁 File Structure (if needed)
/project-folder
│
├── firebase-adminsdk.json       # Your Firebase credential file
├── your_script_name.py          # Main script to run
├── README.md                    # This instruction file
