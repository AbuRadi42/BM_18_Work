from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import sqlite3
from collections import Counter
from datetime import datetime
import base64
import os
import atexit
import face_recognition

app = Flask(__name__)

# Configuration
DATABASE_PATH = 'attendance.db'
BIOMETRIC_PHOTOS_DIR = 'biometric_photos'

# Initialize SQLite database
conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        event_type TEXT,
        timestamp TEXT
    )
''')
conn.commit()

# Load known faces
known_faces = []
known_names = []
for filename in os.listdir(BIOMETRIC_PHOTOS_DIR):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = face_recognition.load_image_file(os.path.join(BIOMETRIC_PHOTOS_DIR, filename))
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(os.path.splitext(filename)[0])

# Function to register event
def register_event(name, event_type):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO attendance (name, event_type, timestamp)
        VALUES (?, ?, ?)
    ''', (name, event_type, timestamp))
    conn.commit()
    print(f"[INFO] Registered: {name} at {timestamp}")

# Buffer for face detection readings
face_buffer = []
last_registered_name = None
last_registered_time = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    global face_buffer, last_registered_name, last_registered_time
    data = request.json

    try:
        frame_data = data['frame'].split(',')[1]
        frame_bytes = base64.b64decode(frame_data)
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Failed to decode frame.")
    except Exception as e:
        print(f"[ERROR] Failed to decode frame: {e}")
        return jsonify({'status': 'error', 'message': 'Invalid frame data'}), 400

    detected_faces = recognize_faces(frame)

    if len(detected_faces) == 0:
        print("[WARNING] No faces detected.")
        return jsonify({'status': 'success', 'faces': []})

    for face in detected_faces:
        if face['name'] != "Unknown":
            face_buffer.append(face['name'])

    if len(face_buffer) >= 9:
        most_common_name, count = Counter(face_buffer).most_common(1)[0]
        current_time = datetime.now()

        if (last_registered_time is None or
            last_registered_name != most_common_name or
            (current_time - last_registered_time).total_seconds() > 300):
            event_type = 'Entry'
            register_event(most_common_name, event_type)
            last_registered_name = most_common_name
            last_registered_time = current_time

        face_buffer = []

    return jsonify({'status': 'success', 'faces': detected_faces})

def recognize_faces(frame):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    detected_faces = []
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]

        detected_faces.append({'x': left, 'y': top, 'w': right - left, 'h': bottom - top, 'name': name})
        print(f"Detected face: {name} at ({left}, {top}, {right}, {bottom})")

    return detected_faces

@app.route('/get_readings', methods=['GET'])
def get_readings():
    cursor.execute('SELECT * FROM attendance ORDER BY timestamp DESC')
    readings = cursor.fetchall()
    return jsonify(readings)

# Clean up the database connection when the application stops
def shutdown():
    conn.close()

atexit.register(shutdown)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
