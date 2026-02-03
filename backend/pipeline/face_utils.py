import os
import cv2
import numpy as np

# Set environment variable to bypass OpenMP conflict
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# Set DeepFace home to D drive
os.environ["DEEPFACE_HOME"] = r"D:\DeepFace_Models"

def get_face_embedding(image_path):
    try:
        from deepface import DeepFace
        # Using VGG-Face as default
        embeddings = DeepFace.represent(img_path=image_path, model_name="VGG-Face", enforce_detection=False)
        if embeddings:
            return embeddings[0]["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
    return None

def verify_faces(img1_path, img2_path):
    try:
        from deepface import DeepFace
        result = DeepFace.verify(img1_path=img1_path, img2_path=img2_path, model_name="VGG-Face", enforce_detection=False)
        return result["verified"], result["distance"]
    except Exception as e:
        print(f"Error verifying faces: {e}")
    return False, 1.0

def check_camera_hiding(image_path):
    """Detects if the camera is covered or if it's too dark."""
    img = cv2.imread(image_path)
    if img is None:
        return True
    
    # Calculate average brightness
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    
    # If average brightness is very low (e.g., < 10 out of 255), it's likely covered
    return avg_brightness < 15

def detect_electronic_devices(image_path):
    """Helper to detect phones, tablets, or laptops using a generic model."""
    try:
        from inference_sdk import InferenceHTTPClient
        CLIENT = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key="hJELY7N0IMKZaP2I0KnY"
        )
        # Using a popular public model for phone detection
        result = CLIENT.infer(image_path, model_id="cell-phone-detection/1") 
        
        prohibited_items = ["cell phone", "phone", "mobile", "laptop", "electronic", "tablet"]
        for pred in result["predictions"]:
            if pred["confidence"] > 0.4:
                return True, pred["class"]
    except Exception as e:
        print(f"Object Detection Error: {e}")
    return False, None

def analyze_proctoring_frame(live_img_path, ref_img_path):
    """
    Analyzes a proctoring frame for:
    1. Camera Hiding
    2. Face Presence (None vs Some)
    3. Multi-face Detection (>1 face)
    4. Electronic Device Detection (Phone/Laptop)
    5. Face Matching (Matches reference)
    """
    try:
        # Check 1: Camera Hiding
        hiding = check_camera_hiding(live_img_path)
        print(f"DEBUG: Camera Hiding Check -> {hiding}")
        if hiding:
            return "CAMERA_HIDDEN", None

        # Check 2: Electronic Devices
        device_found, device_name = detect_electronic_devices(live_img_path)
        print(f"DEBUG: Device Check -> Found: {device_found}, Name: {device_name}")
        if device_found:
            return "PHONE_DETECTED", device_name

        from deepface import DeepFace
        
        # Check 3: Detect and count faces
        faces = DeepFace.extract_faces(img_path=live_img_path, detector_backend='opencv', enforce_detection=False)
        
        face_count = 0
        for f in faces:
             if f['confidence'] > 0.4: 
                 face_count += 1
        
        print(f"DEBUG: Face Count -> {face_count}")

        if face_count == 0:
            return "NO_FACE", None
        
        if face_count > 1:
            return "MULTI_FACE", None

        # Check 4: Perform Verification
        verified, distance = verify_faces(live_img_path, ref_img_path)
        print(f"DEBUG: Face Verify -> {verified} (Distance: {distance})")
        if verified:
            return "SUCCESS", distance
        else:
            return "MISMATCH", distance

    except Exception as e:
        print(f"Analysis Error: {e}")
        return "ERROR", str(e)
