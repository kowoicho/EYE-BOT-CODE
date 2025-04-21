import cv2
import dlib
from scipy.spatial import distance
from picamera2 import Picamera2
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client
import csv
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

# AES encryption setup
key = os.urandom(32)  # 256-bit AES key
iv = os.urandom(16)   # 128-bit IV

def aes_encrypt(plain_text: str) -> str:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_text = plain_text + (16 - len(plain_text) % 16) * ' '
    encrypted = encryptor.update(padded_text.encode()) + encryptor.finalize()
    return base64.b64encode(encrypted).decode()

def aes_decrypt(encrypted_text: str) -> str:
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    encrypted_data = base64.b64decode(encrypted_text)
    decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
    return decrypted.decode().rstrip()

# TODO: Replace with the path to your shape predictor file
shape_predictor_path = "path/to/shape_predictor_68_face_landmarks.dat"

# Initialize dlib's face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor_path)

# Initialize Pi Camera
picam2 = Picamera2()
picam2.start()

# TODO: Replace with path to your Firebase service account key
cred = credentials.Certificate("path/to/firebase-service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# TODO: Replace with your Twilio credentials and phone numbers
account_sid = "your_twilio_account_sid"
auth_token = "your_twilio_auth_token"
twilio_client = Client(account_sid, auth_token)
twilio_phone_number = "your_twilio_phone_number"
destination_phone_number = "receiver_phone_number"

# Eye Aspect Ratio threshold
EAR_THRESHOLD = 0.24
blink_count = 0
blink_detected = False

# Blink thresholds (per minute)
drowsiness_range = (1, 7)
tiredness_threshold = 21

interval_start_time = time.time()

def calculate_ear(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

LEFT_EYE_POINTS = list(range(36, 42))
RIGHT_EYE_POINTS = list(range(42, 48))

# TODO: Optional - Replace with desired CSV save path
csv_file_path = "eyetracking_data.csv"

if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "alert_message", "blink_count"])

while True:
    frame = picam2.capture_array()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = detector(frame_rgb)

    for face in faces:
        landmarks = predictor(frame_rgb, face)
        left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in LEFT_EYE_POINTS]
        right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in RIGHT_EYE_POINTS]
        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)
        ear = (left_ear + right_ear) / 2.0

        if ear < EAR_THRESHOLD and not blink_detected:
            blink_count += 1
            blink_detected = True
        elif ear >= EAR_THRESHOLD:
            blink_detected = False

        for (x, y) in left_eye + right_eye:
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    elapsed_time = time.time() - interval_start_time

    if elapsed_time >= 60:
        alert_message = ""

        if drowsiness_range[0] <= blink_count <= drowsiness_range[1]:
            alert_message = f"Drowsiness detected, Blink Count: {blink_count}"
        elif blink_count >= tiredness_threshold:
            alert_message = f"Tiredness detected, Blink Count: {blink_count}"

        if alert_message:
            encrypted_message = aes_encrypt(alert_message)
            decrypted_message = aes_decrypt(encrypted_message)

            doc_ref = db.collection("alerts").document(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            doc_ref.set({
                "alert_message": decrypted_message,
                "blink_count": blink_count,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            message = twilio_client.messages.create(
                body=decrypted_message,
                from_=twilio_phone_number,
                to=destination_phone_number
            )

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Alert Sent: {decrypted_message}")

        blink_count = 0
        interval_start_time = time.time()
