import cv2
import os
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="hJELY7N0IMKZaP2I0KnY"
)

MODEL_ID = "id_card_detection-dbzys/1"

def crop_id_card(image_path, output_dir="outputs/id_cards"):
    os.makedirs(output_dir, exist_ok=True)

    img = cv2.imread(image_path)
    if img is None:
        return None

    try:
        result = CLIENT.infer(image_path, model_id=MODEL_ID)
    except Exception as e:
        print(f"Roboflow Inference Error (Model 1): {e}")
        return None

    if len(result["predictions"]) == 0:
        return None

    pred = result["predictions"][0]

    x1 = int(pred["x"] - pred["width"] / 2)
    y1 = int(pred["y"] - pred["height"] / 2)
    x2 = int(pred["x"] + pred["width"] / 2)
    y2 = int(pred["y"] + pred["height"] / 2)

    crop = img[y1:y2, x1:x2]

    out_path = os.path.join(output_dir, "id_card.jpg")
    cv2.imwrite(out_path, crop)

    return out_path
