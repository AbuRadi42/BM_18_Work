# AI and Data Science Innovations Portfolio

This portfolio showcases a collection of AI and Data Science projects, each addressing unique challenges and leveraging various technologies to deliver innovative solutions.

## Project 1A: Vehicle Presence Detection System with openALPR (2019)

### Overview
- **Objective**: Develop a real-time vehicle tracking system using license plate recognition for corporate entrances and parking areas.
- **Technologies**: OpenALPR, OpenCV
- **Implementation**: Detects and logs vehicle entries/exits, enhancing security and operational efficiency.
- **Impact**: Improved monitoring in high-traffic areas, particularly in the City of Johannesburg and Gauteng Province, South Africa.

### Technical Details
- **Video Frame Capture**: Uses OpenCV to capture video frames.
- **License Plate Detection**: Employs edge detection and pattern recognition.
- **OCR Processing**: Extracts alphanumeric characters from detected plates.
- **Accuracy Buffer**: Collects readings from multiple frames to mitigate errors.
- **Event Registration**: Logs plate numbers with associated events, reducing redundant entries.

### Challenges
- High configuration demands and sensitivity to license plate orientation.

## Project 1B: Haar Cascades Face ID Attendance Registration System (2020)

### Overview
- **Objective**: Develop a lightweight facial recognition attendance system using Haar Cascades.
- **Technologies**: Haar Cascades, OpenCV, face_recognition library, Python/Flask/SQLite
- **Implementation**: Identifies individuals from video feeds and logs attendance records.
- **Impact**: Enhanced accuracy and efficiency in tracking personnel movements.

### Technical Details
- **Video Frame Capture**: Captures video frames using OpenCV.
- **Face Detection**: Uses Haar Cascades for initial detection, followed by the face_recognition library for improved accuracy.
- **Attendance Logging**: Logs attendance records in an SQLite database.

### Challenges
- Privacy concerns and the need for compliance with regulations.

## Project 2: Voxalyze (formerly OctaPy) - Customer Call Analysis (2021)

### Overview
- **Objective**: Analyze customer calls to extract key information and evaluate sentiment.
- **Technologies**: Python, Flask, Pandas, SQLite, Pydub, LibROSA, Speech-to-text APIs
- **Implementation**: Features a RESTful back-end for call recording, activity logging, and sentiment analysis.
- **Impact**: Showcased potential to enhance customer engagement and operational efficiency.

### Technical Details
- **Audio Processing**: Uses Pydub and LibROSA for segmentation.
- **Speech-to-Text**: Converts audio data to text for information extraction and sentiment analysis.
- **UI Design**: Provides a structured dashboard for analyzing call interactions.

### Challenges
- Market shifts towards LLM-based NLP models rendered the solution less competitive.

## Project 3: PN1 - AI Dog Translator (2025)

### Overview
- **Objective**: Develop a PWA to analyze canine behavior and predict basic emotions.
- **Technologies**: TensorFlow, HTML5, TailwindCSS, Vanilla JavaScript, IndexedDB
- **Implementation**: Utilizes visual and acoustic data to predict emotions based on the Russell model.
- **Impact**: Potential to enhance human-animal communication and aid in pet care and wildlife research.

### Technical Details
- **Data Analysis**: Employs TensorFlow to analyze visual and acoustic data.
- **Emotion Prediction**: Uses a neural network to predict emotions based on the Russell model.
- **User Experience**: Provides real-time emotion analysis using HTML5 and TailwindCSS.

### Challenges
- The project is currently under development, with more details to be shared during the oral exam.

## References
- Mittal, A. (2020). Haar Cascades, Explained. Analytics Vidhya.
- Crisp, C. (2021). Back-End Technical Requirements v1.27.
- Russell, J. A. (1980). A circumplex model of affect. Journal of Personality and Social Psychology.