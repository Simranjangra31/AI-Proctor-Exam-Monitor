import os
import cv2
from inference_sdk import InferenceHTTPClient

# ==============================
# CONFIG
# ==============================
API_KEY = "R8nCdoW0KeNM1EscT0Vz"   # <-- replace this
MODEL_ID = "id_card_detection-dbzys/1"

INPUT_DIR = "input_images"
OUTPUT_DIR = "cropped_id_cards"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=API_KEY
)

# ==============================
# PROCESS IMAGES
# ==============================
for image_name in os.listdir(INPUT_DIR):
    if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    image_path = os.path.join(INPUT_DIR, image_name)
    image = cv2.imread(image_path)

    if image is None:
        print(f"❌ Could not read {image_name}")
        continue

    h, w, _ = image.shape

    # Run inference
    result = CLIENT.infer(image_path, model_id=MODEL_ID)

    if "predictions" not in result or len(result["predictions"]) == 0:
        print(f"⚠️ No ID card detected in {image_name}")
        continue

    # Take highest confidence detection
    pred = max(result["predictions"], key=lambda x: x["confidence"])

    # Convert center-based bbox to corners
    x_center, y_center = pred["x"], pred["y"]
    bw, bh = pred["width"], pred["height"]

    x1 = int(x_center - bw / 2)
    y1 = int(y_center - bh / 2)
    x2 = int(x_center + bw / 2)
    y2 = int(y_center + bh / 2)

    # Clamp values
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    crop = image[y1:y2, x1:x2]

    if crop.size == 0:
        print(f"❌ Empty crop for {image_name}")
        continue

    output_path = os.path.join(OUTPUT_DIR, image_name)
    cv2.imwrite(output_path, crop)

    print(f"✅ Cropped ID card saved: {image_name}")

print("\n🎉 Done! All ID cards cropped.")
