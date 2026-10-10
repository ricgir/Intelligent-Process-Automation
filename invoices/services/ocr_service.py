import os
import shutil
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Auto-detect tesseract binary path
tesseract_path = shutil.which("tesseract") or "/usr/bin/tesseract"
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path


def extract_text_from_file(file_path):
    """
    Extracts text from an image or PDF file path.
    Supports .pdf, .png, .jpg, .jpeg file extensions.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    if ext == ".pdf":
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            text = ""

        # Fallback to OCR via image conversion if pdfplumber returns empty text
        if not text.strip():
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img, config="--oem 3 --psm 6") + "\n"

    elif ext in [".png", ".jpg", ".jpeg"]:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, config="--oem 3 --psm 6")

    else:
        raise ValueError("Unsupported file format. Only PDF, PNG, JPG, and JPEG files are supported.")

    if not text.strip():
        raise ValueError("OCR failed to extract any readable text from the document.")

    return text.strip()
