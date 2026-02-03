import cv2
import os
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="hJELY7N0IMKZaP2I0KnY"
)

MODEL_ID = "prn_photo_detection/1"   # your trained model‑2

def detect_id_fields(id_card_path, output_dir="outputs/fields"):
    os.makedirs(output_dir, exist_ok=True)

    img = cv2.imread(id_card_path)
    if img is None:
        return {"prn": None, "photo": None}

    try:
        result = CLIENT.infer(id_card_path, model_id=MODEL_ID)
    except Exception as e:
        print(f"Roboflow Inference Error (Model 2): {e}")
        return {"prn": None, "photo": None}
    
    fields = {"prn": None, "photo": None}

    for pred in result["predictions"]:
        class_name = pred["class"]
        if class_name in ["prn", "photo"]:
            x1 = int(max(0, pred["x"] - pred["width"] / 2))
            y1 = int(max(0, pred["y"] - pred["height"] / 2))
            x2 = int(min(img.shape[1], pred["x"] + pred["width"] / 2))
            y2 = int(min(img.shape[0], pred["y"] + pred["height"] / 2))

            crop = img[y1:y2, x1:x2]
            filename = f"{class_name}_field.jpg"
            out_path = os.path.join(output_dir, filename)
            cv2.imwrite(out_path, crop)
            fields[class_name] = out_path

    return fields
