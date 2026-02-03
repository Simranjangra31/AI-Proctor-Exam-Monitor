// Exam State
let currentQuestionIndex = 0;
const questions = [
    { text: "What is the primary purpose of YOLOv11 in this project?", options: ["Database management", "Object detection and cropping", "Sending emails", "Styling CSS"], answer: 1 },
    { text: "Which library is used for Face Recognition analysis?", options: ["Pandas", "Scikit-Learn", "DeepFace", "Matplotlib"], answer: 2 },
    { text: "PRN stands for?", options: ["Personal Record Number", "Permanent Registration Number", "Public Relation Network", "Private Root Name"], answer: 1 },
    { text: "FastAPI is built on top of which library?", options: ["Flask", "Django", "Starlette", "Express.js"], answer: 2 },
];

// Elements
const qText = document.getElementById('q-text');
const optionsContainer = document.getElementById('options-container');
const qCount = document.getElementById('q-count');
const nextBtn = document.getElementById('next-btn');
const prevBtn = document.getElementById('prev-btn');
const timerEl = document.getElementById('exam-timer');
const proctorVideo = document.getElementById('proctor-video');
const alertLogs = document.getElementById('alert-logs');

// Initialization
async function initExam() {
    // 1. Recover student data from SessionStorage
    const studentData = JSON.parse(sessionStorage.getItem('studentData'));
    if (!studentData) {
        window.location.href = '/';
        return;
    }
    document.getElementById('student-name').innerText = studentData.name || "Test Student";
    document.getElementById('student-prn').innerText = `PRN: ${studentData.prn}`;

    // 2. Start Proctoring
    await startProctoring();

    // 3. Load First Question
    loadQuestion(0);
    startTimer(3600); // 60 mins

    // 4. Lock Browser Logic
    setupBrowserLock();
}

async function startProctoring() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        proctorVideo.srcObject = stream;
        addLog("Hardware permissions granted.", "success");

        // Start continuous face verification every 5 seconds for responsive proctoring
        setInterval(verifyProctoringFace, 5000);
    } catch (err) {
        console.error("Proctoring error:", err);
        addLog("Camera/Mic Permission Denied!", "error");
    }
}

async function verifyProctoringFace() {
    console.log("Checking proctoring status...");
    const studentData = JSON.parse(sessionStorage.getItem('studentData'));
    if (!studentData || !proctorVideo.videoWidth) {
        console.warn("Proctoring skipped: Video not ready or student data missing.");
        return;
    }

    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = proctorVideo.videoWidth;
    canvas.height = proctorVideo.videoHeight;
    context.drawImage(proctorVideo, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('file', blob, "proctor_frame.jpg");
        formData.append('prn', studentData.prn);

        try {
            const response = await fetch('/verify-proctored-face', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.status === 'success') {
                const verdict = result.data.verdict;
                console.log("Proctoring Verdict:", verdict);
                if (verdict === 'SUCCESS') {
                    updateFaceIndicator(true, "Authorized");
                } else if (verdict === 'NO_FACE') {
                    addLog("Security Alert: No face detected at monitor!", "warning");
                    updateFaceIndicator(false, "No Face Detected");
                } else if (verdict === 'MULTI_FACE') {
                    addLog("Security Alert: Multiple persons detected at monitor!", "warning");
                    updateFaceIndicator(false, "Multiple Faces Detected");
                } else if (verdict === 'MISMATCH') {
                    addLog("Security Alert: Face mismatched with registered profile!", "warning");
                    updateFaceIndicator(false, "Identity Mismatch");
                } else if (verdict === 'CAMERA_HIDDEN') {
                    addLog("CRITICAL: Camera is hidden or obscured!", "warning");
                    updateFaceIndicator(false, "Camera Obscured");
                } else if (verdict === 'PHONE_DETECTED') {
                    addLog("CRITICAL: Electronic device detected in frame!", "warning");
                    updateFaceIndicator(false, "Electronic Device Detected");
                }
            }
        } catch (err) {
            console.error("Proctoring verification failed:", err);
        }
    }, 'image/jpeg');
}

function updateFaceIndicator(verified, message) {
    const indicator = document.getElementById('face-indicator');
    if (indicator) {
        indicator.innerHTML = verified ?
            `<i class="fas fa-user-check" style="color: #28a745;"></i> ${message}` :
            `<i class="fas fa-user-times" style="color: #dc3545;"></i> ${message}`;
    }
}

function loadQuestion(index) {
    currentQuestionIndex = index;
    const q = questions[index];
    qCount.innerText = `Question ${index + 1} of ${questions.length}`;
    qText.innerText = q.text;

    optionsContainer.innerHTML = '';
    q.options.forEach((opt, i) => {
        const div = document.createElement('div');
        div.className = 'option-item';
        div.innerHTML = `<span class="opt-label">${String.fromCharCode(65 + i)}</span> <span>${opt}</span>`;
        div.onclick = () => {
            document.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
            div.classList.add('selected');
        };
        optionsContainer.appendChild(div);
    });

    prevBtn.disabled = index === 0;
    nextBtn.innerText = index === questions.length - 1 ? "Finish" : "Next";
}

function setupBrowserLock() {
    // Detect Tab Switch
    window.addEventListener('blur', () => {
        addLog("Security Alert: Tab switched or window minimized!", "warning");
    });

    window.addEventListener('focus', () => {
        addLog("Security Info: Re-entered exam screen.", "info");
    });

    // Detect Right Click
    document.addEventListener('contextmenu', (e) => e.preventDefault());

    // Fullscreen Prompt (Self-executing if possible or on click)
    document.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.warn(`Error attempting to enable fullscreen: ${err.message}`);
            });
        }
    }, { once: true });
}

async function addLog(msg, type) {
    const alertBox = document.createElement('div');
    alertBox.className = `alert-item alert-${type === 'warning' ? 'warning' : 'info'}`;
    alertBox.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${msg}`;
    alertLogs.prepend(alertBox);

    // Sync with backend
    const studentData = JSON.parse(sessionStorage.getItem('studentData'));
    if (studentData && type === 'warning') {
        try {
            await fetch('/log-alert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prn: studentData.prn,
                    type: type,
                    description: msg
                })
            });
        } catch (err) {
            console.error("Alert sync failed:", err);
        }
    }
}

function startTimer(duration) {
    let timer = duration, minutes, seconds;
    setInterval(() => {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        timerEl.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            alert("Time Up! Submitting Exam.");
            window.location.href = '/';
        }
    }, 1000);
}

// Navigation
nextBtn.onclick = () => {
    if (currentQuestionIndex < questions.length - 1) {
        loadQuestion(currentQuestionIndex + 1);
    } else {
        alert("Exam Submitted Successfully!");
        window.location.href = '/';
    }
};

prevBtn.onclick = () => {
    if (currentQuestionIndex > 0) {
        loadQuestion(currentQuestionIndex - 1);
    }
};

initExam();
