// DOM Elements
const idFileInput = document.getElementById('id-file');
const idWebcam = document.getElementById('id-id-webcam'); // Fallback check
const idWebcamEl = document.getElementById('id-webcam');
const mainWebcamEl = document.getElementById('webcam'); // Step 2 webcam
const captureIdBtn = document.getElementById('capture-id-btn');
const processBtn = document.getElementById('process-id-btn');
const toggleWebcam = document.getElementById('toggle-webcam');
const toggleUpload = document.getElementById('toggle-upload');
const idWebcamContainer = document.getElementById('id-webcam-container');
const dropZone = document.getElementById('drop-zone');
const idPreview = document.getElementById('id-preview');
const idPreviewContainer = document.getElementById('id-preview-container');
const loaderOverlay = document.getElementById('loader-overlay');
const resultsArea = document.getElementById('results-area');
const captureProctorBtn = document.getElementById('capture-btn');
const verStatus = document.getElementById('verification-status');

let idStream = null;

// Helper to show/hide loader
function showLoader(show) {
    loaderOverlay.style.display = show ? 'flex' : 'none';
}

// Initialize Webcam Stream
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        idStream = stream;
        idWebcamEl.srcObject = stream;
        mainWebcamEl.srcObject = stream;
        document.getElementById('id-detection-status').innerHTML = '<i class="fas fa-check-circle"></i> Camera Active';
    } catch (err) {
        console.error("Camera access error:", err);
        document.getElementById('id-detection-status').innerHTML = '<i class="fas fa-exclamation-triangle"></i> Camera Error';
    }
}

// Mode Toggling (Webcam vs Upload)
toggleWebcam.onclick = () => {
    toggleWebcam.classList.add('active');
    toggleUpload.classList.remove('active');
    idWebcamContainer.style.display = 'block';
    dropZone.style.display = 'none';
    idPreviewContainer.style.display = 'none';
    captureIdBtn.style.display = 'block';
    processBtn.style.display = 'none';
};

toggleUpload.onclick = () => {
    toggleUpload.classList.add('active');
    toggleWebcam.classList.remove('active');
    idWebcamContainer.style.display = 'none';
    dropZone.style.display = 'block';
    captureIdBtn.style.display = 'none';
    processBtn.style.display = 'block';
};

// Handle File Drop/Selection
dropZone.onclick = () => idFileInput.click();

idFileInput.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (re) => {
            idPreview.src = re.target.result;
            idPreviewContainer.style.display = 'block';
            dropZone.style.display = 'none';
        }
        reader.readAsDataURL(file);
    }
};

// Verify PRN from Uploaded File
processBtn.onclick = async () => {
    const file = idFileInput.files[0];
    if (!file) {
        alert("Please upload an ID card photo.");
        return;
    }
    await uploadAndProcessID(file);
};

// Capture and Verify PRN from Webcam
captureIdBtn.onclick = async () => {
    const canvas = document.getElementById('id-canvas');
    const context = canvas.getContext('2d');
    canvas.width = idWebcamEl.videoWidth;
    canvas.height = idWebcamEl.videoHeight;
    context.drawImage(idWebcamEl, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        const file = new File([blob], "captured_id.jpg", { type: "image/jpeg" });
        await uploadAndProcessID(file);
    }, 'image/jpeg');
};

async function uploadAndProcessID(file) {
    showLoader(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/detect-id', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (result.status === 'success') {
            updateResults(result.data);

            // Unlock Step 2 if PRN is matched in Database
            if (result.data.verified_student) {
                sessionStorage.setItem('studentData', JSON.stringify({
                    name: result.data.verified_student.name,
                    prn: result.data.prn
                }));

                captureProctorBtn.disabled = false;
                verStatus.innerHTML = '<i class="fas fa-camera"></i> Ready for Profiling';
                alert(`PRN Matched: ${result.data.verified_student.name}. Please take your profile photo (Step 2).`);
            }
        } else {
            alert(result.message || "PRN detection failed. Please try again with a clearer view.");
        }
    } catch (err) {
        console.error("Processing error:", err);
        alert("Server communication error.");
    } finally {
        showLoader(false);
    }
}

// Step 2: Capture Proctoring Reference Photo
captureProctorBtn.onclick = async () => {
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    canvas.width = mainWebcamEl.videoWidth;
    canvas.height = mainWebcamEl.videoHeight;
    context.drawImage(mainWebcamEl, 0, 0, canvas.width, canvas.height);

    showLoader(true);
    canvas.toBlob(async (blob) => {
        const studentData = JSON.parse(sessionStorage.getItem('studentData'));
        const formData = new FormData();
        formData.append('file', blob, "proctor_ref.jpg");
        formData.append('prn', studentData.prn);

        try {
            const response = await fetch('/save-reference', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.status === 'success') {
                alert("Profile Registered Successfully!");
                window.location.href = "/exam?prn=" + studentData.prn;
            } else {
                alert("Profile registration failed: " + result.message);
            }
        } catch (err) {
            console.error("Reference save error:", err);
            alert("Reference save server error.");
        } finally {
            showLoader(false);
        }
    }, 'image/jpeg');
};

function updateResults(data) {
    resultsArea.style.display = 'block';
    document.getElementById('res-prn').innerText = data.prn || "Not Detected";
    document.getElementById('res-conf').innerText = `${(data.confidence * 100).toFixed(1)}%`;

    const dbBadge = document.getElementById('res-db-status');
    const summary = document.getElementById('summary-content');

    if (data.verified_student) {
        dbBadge.innerText = "Access Granted";
        dbBadge.className = "status-badge verified";
        summary.innerHTML = `
            <p style="color: #28a745; font-weight: 600;">Match Found: ${data.verified_student.name}</p>
            <p>Your PRN (${data.prn}) is successfully verified. Please proceed to Step 2 for proctoring setup.</p>
        `;
    } else {
        dbBadge.innerText = "Access Denied";
        dbBadge.className = "status-badge failed";
        summary.innerHTML = `
            <p style="color: #dc3545; font-weight: 600;">PRN Not Registered</p>
            <p>The detected PRN (${data.prn}) was not found in our records.</p>
        `;
    }
}

// Start camera on load
startWebcam();
