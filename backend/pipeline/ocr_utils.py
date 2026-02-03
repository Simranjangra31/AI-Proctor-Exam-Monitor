import cv2
import easyocr
import re
import os

# Set environment variable to bypass OpenMP conflict
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

MODEL_PATH = r"D:\EasyOCR_Models"
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        print("Initializing EasyOCR Reader...")
        # Since PRNs are printed digits, we use English context
        _reader = easyocr.Reader(['en'], model_storage_directory=MODEL_PATH, gpu=False)
    return _reader

def preprocess_for_ocr(image_path):
    """Prepares printed text for better OCR accuracy."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    # 1. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Rescale (Zoom in) if the text is too small
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # 3. Apply Otsu's Binarization to make text pure black and background pure white
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Save the processed image for OCR
    temp_path = image_path.replace(".jpg", "_proc.jpg")
    cv2.imwrite(temp_path, thresh)
    return temp_path

def extract_prn(image_path):
    # Apply preprocessing first
    processed_path = preprocess_for_ocr(image_path)
    reader = get_reader()
    
    # Restrict OCR to digits only for printed PRNs
    results = reader.readtext(processed_path or image_path, allowlist='0123456789')

    for bbox, text, conf in results:
        text = text.strip()
        # Printed PRNs usually have high confidence
        if conf > 0.6 and re.search(r"\d{7,15}", text):
            return text, float(conf)

    return None, 0.0
