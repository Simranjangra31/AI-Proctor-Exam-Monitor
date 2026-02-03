from .model1_crop_id import crop_id_card
from .model2_detect_fields import detect_id_fields
from .ocr_utils import extract_prn

def run_pipeline(input_image_path):
    id_card = crop_id_card(input_image_path)
    if not id_card:
        return {"status": "error", "message": "ID card not detected"}

    fields = detect_id_fields(id_card)
    prn_crop = fields.get("prn")
    photo_crop = fields.get("photo")

    if not prn_crop:
        return {"status": "error", "message": "PRN not detected"}

    prn, confidence = extract_prn(prn_crop)

    return {
        "status": "success",
        "prn": prn,
        "confidence": confidence,
        "photo_path": photo_crop
    }

    
