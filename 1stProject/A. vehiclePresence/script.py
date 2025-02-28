from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import sqlite3
from collections import Counter
from datetime import datetime
import base64
import subprocess
import json
import atexit

app = Flask(__name__)

# Configuration
ENTRY_MODE = True  # Set to False for leave mode
DATABASE_PATH = 'license_plates.db'
ALPR_CONFIG_PATH = '/etc/openalpr/openalpr.conf'  # Update with your OpenALPR config path
ALPR_RUNTIME_DATA_PATH = '/usr/local/share/openalpr/runtime_data'  # Update with your runtime data path

# Initialize SQLite database
conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_plate TEXT,
        event_type TEXT,
        timestamp TEXT
    )
''')
conn.commit()

# Function to register event
def register_event(license_plate, event_type):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO events (license_plate, event_type, timestamp)
        VALUES (?, ?, ?)
    ''', (license_plate, event_type, timestamp))
    conn.commit()

# Buffer for license plate readings
plate_buffer = []
last_registered_plate = None
last_registered_time = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    global plate_buffer, last_registered_plate, last_registered_time
    data = request.json

    # Decode the incoming frame
    frame_data = data['frame'].split(',')[1]
    frame_bytes = base64.b64decode(frame_data)
    frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

    # Save the frame to a temporary file
    temp_frame_path = "/tmp/temp_frame.jpg"
    cv2.imwrite(temp_frame_path, frame)

    # Call OpenALPR CLI tool with the JSON flag
    command = [
        'alpr', '-j', '-c', 'eu', '-n', '1', '--config', ALPR_CONFIG_PATH, temp_frame_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        return jsonify({'status': 'error', 'message': 'ALPR CLI error', 'error': result.stderr}), 500

    try:
        results = json.loads(result.stdout)
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'Invalid JSON from ALPR CLI'}), 500

    # Process ALPR results if available
    if 'results' in results:
        for plate in results['results']:
            plate_buffer.append(plate['plate'])

    # If buffer is full, determine the most prominent plate
    if len(plate_buffer) >= 9:
        most_common_plate = Counter(plate_buffer).most_common(1)[0][0]
        current_time = datetime.now()

        # If it's the first event or more than 5 minutes have passed since last registration
        if (last_registered_time is None or 
            last_registered_plate != most_common_plate or 
            (current_time - last_registered_time).total_seconds() > 300):
            event_type = 'Entry' if ENTRY_MODE else 'Leave'
            register_event(most_common_plate, event_type)
            last_registered_plate = most_common_plate
            last_registered_time = current_time

        plate_buffer = []  # Clear the buffer

    return jsonify({'status': 'success'})

@app.route('/get_readings', methods=['GET'])
def get_readings():
    cursor.execute('SELECT * FROM events ORDER BY timestamp DESC')
    readings = cursor.fetchall()
    return jsonify(readings)

# Clean up the database connection when the application stops
def shutdown():
    conn.close()

atexit.register(shutdown)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
