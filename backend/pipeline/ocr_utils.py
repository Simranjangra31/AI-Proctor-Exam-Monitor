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

def extract_prn(image_path):
    """Detects printed PRN numbers using EasyOCR directly."""
    reader = get_reader()
    
    # Restrict OCR to digits only for printed PRNs for higher speed/accuracy
    results = reader.readtext(image_path, allowlist='0123456789')

    for bbox, text, conf in results:
        text = text.strip()
        # Printed PRNs are usually very clear
        if conf > 0.5 and re.search(r"\d{7,15}", text):
            return text, float(conf)

    return None, 0.0
