from io import BytesIO

import pytesseract
from PIL import Image


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from an image using Tesseract OCR.
    """
    image = Image.open(BytesIO(image_bytes))
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    return pytesseract.image_to_string(
        image,
        lang="eng",
        config="--psm 6"
    ).strip()