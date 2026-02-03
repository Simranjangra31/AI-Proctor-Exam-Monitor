# AI Proctor Exam Monitor 🛡️🎓

A secure, AI-powered student examination portal featuring robust identity verification and real-time proctoring. This project automates student authentication through ID card analysis and ensures exam integrity using continuous AI-based facial monitoring.

## 🚀 Features

### 🔍 1. Identity Verification (Phase 1 & 2)
*   **PRN Extraction**: Uses **EasyOCR** with custom image preprocessing (Grayscale + Thresholding) for high-accuracy extraction of Permanent Registration Numbers (PRNs) from printed ID cards.
*   **Database Verification**: Automatically checks extracted PRNs against a SQLite student database.
*   **Profile Registration**: Verified students capture a high-quality reference photo used for session-long proctoring.

### 🛡️ 2. Real-time AI Proctoring (Phase 3 & 4)
*   **Continuous Authentication**: Checks student's identity every 5 seconds against the registration photo using **DeepFace**.
*   **Absence Detection**: Flags if the student leaves the monitor or hides their face.
*   **Multi-face Detection**: Detects if more than one person enters the camera frame.
*   **Electronic Device Detection**: Uses **YOLOv11** to detect prohibited items like cell phones, laptops, and tablets.
*   **Camera Hiding Detection**: Detects if the student attempts to obscure the camera lens.

### 💻 3. Secure Exam Environment
*   **Browser Lock**: Detects and logs tab switching or window minimization.
*   **Fullscreen Enforcement**: Encourages students to stay within the dedicated exam UI.
*   **Dynamic Alert Dashboard**: Real-time display of proctoring violations to both the student and for backend logging.

---

## 🛠️ Technology Stack
*   **Backend**: FastAPI (Python)
*   **Frontend**: Vanilla HTML5, CSS3, JavaScript (Streamlit-inspired design)
*   **Computer Vision**: OpenCV, DeepFace, EasyOCR, YOLOv11 (via Roboflow)
*   **Database**: SQLAlchemy with SQLite
*   **Server**: Uvicorn

---

## 📦 Installation & Setup

### Prerequisites
*   Python 3.10+
*   Webcam & Microphone access
*   D: Drive (The project is configured to store large ML models on `D:\DeepFace_Models`)

### 1. Clone the Repository
```powershell
git clone https://github.com/Simranjangra31/AI-Proctor-Exam-Monitor.git
cd AI-Proctor-Exam-Monitor
```

### 2. Environment Setup
Create a virtual environment and install dependencies:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
*(Note: Ensure you have `KMP_DUPLICATE_LIB_OK=TRUE` set in your environment if running on Windows)*

### 3. Initialize Database
Initialize the student records and proctoring logs:
```powershell
cd backend
python manage_db.py list  # Check existing students
python manage_db.py add <PRN> "<Student Name>"  # Add new students
```

### 4. Run the Application
```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Access the portal at: `http://127.0.0.1:8000`

---

## 📂 Project Structure
```text
AI-Proctor-Exam-Monitor/
├── backend/
│   ├── main.py              # API Endpoints & Fast API config
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # Database schemas (Students, Alerts)
│   ├── manage_db.py         # Utility script for student management
│   ├── pipeline/            # AI Pipeline components
│   │   ├── ocr_utils.py     # PRN extraction logic
│   │   ├── face_utils.py    # Face matching & proctoring AI
│   │   └── pipeline.py      # Core verification workflow
│   └── static/              # Frontend assets (HTML, CSS, JS)
├── .gitignore
└── README.md
```

## 📜 License
This project is developed for educational and proctoring purposes. Use responsibly.
---
**Maintained by**: [Simran Jangra](https://github.com/Simranjangra31) 👩‍💻
