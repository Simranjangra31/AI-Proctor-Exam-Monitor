AI Proctor Exam Monitor

This project is a secure student exam portal that uses AI to check identities and monitor the exam in real time. I built this to make sure the right student is taking the test and that they follow the rules.

Features

Identity Verification
PRN Extraction: I used EasyOCR to read PRN numbers directly from printed ID cards for fast and reliable extraction.
Database Check: The system checks if the PRN exists in my SQLite database.
Photo Registration: Once verified, students take a profile photo which is used to monitor them during the exam.

Real time AI Proctoring
Same Person Check: Every 5 seconds it uses DeepFace to make sure the student at the monitor is the same person who registered.
Absence Detection: It flags if the student leaves their seat or covers the camera.
Multiple Person Detection: It detects if more than one person is visible in the frame.
Phone Detection: I used YOLOv11 to detect phones, laptops, and tablets.
Camera Hiding: It flags if someone tries to hide the camera or if it gets dark.

Exam Security
It detects if you switch tabs or minimize the window during the test.
It forces a fullscreen mode for the exam.
There is a live alert dashboard that shows if any security rules are broken.

Technical Parts
Backend: FastAPI
Frontend: HTML, CSS, JavaScript 
AI Libraries: OpenCV, DeepFace, EasyOCR, YOLOv11 
Database: SQLite

How to Setup

Prerequisites
You need Python 10 or newer.
A webcam and microphone.
A D drive because the ML models are stored in D:\DeepFace_Models.

Installation
1. Clone the project from GitHub.
2. Create a virtual environment and activate it.
3. Install all libraries from the requirements file.
4. Set KMP_DUPLICATE_LIB_OK=TRUE in your environment settings if you are on Windows.

Setup Database
Run manage_db.py to see students or add new ones.
python manage_db.py list
python manage_db.py add (PRN) (Name)

Start the Server
Run uvicorn main:app --reload --host 127.0.0.1 --port 8000
Open http://127.0.0.1:8000 in your browser.

Project Folders
The main code is in the backend folder.
AI logic for faces and OCR is in backend/pipeline.
The exam pages and styles are in backend/static.

Created by Simran Jangra
