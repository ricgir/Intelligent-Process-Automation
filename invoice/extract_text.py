import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def extract_text(file_path):
    text = ""
    
    if file_path.lower().endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"

        
        if not text.strip():
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img, config="--oem 3 --psm 6") + "\n"

    elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, config="--oem 3 --psm 6")

    else:
        raise ValueError("Unsupported file format. Only PDFs and PNG, JPEG, JPG images are allowed.")

    return text
