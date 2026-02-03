import easyocr
import os
import sys

# Set environment variable to bypass OpenMP conflict
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

MODEL_PATH = r"D:\EasyOCR_Models"

print(f"Starting model download (quiet mode) to {MODEL_PATH}...")
try:
    # Disable verbose to avoid progress bar encoding issues
    reader = easyocr.Reader(['en'], download_enabled=True, verbose=False, model_storage_directory=MODEL_PATH)
    print("Models ready!")
except Exception as e:
    print(f"Error during download or init: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
