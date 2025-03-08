# import requests
# import base64
# import re
# from PIL import Image
# import pytesseract
# import argparse
# import cv2
# import os
# import imutils
# import pdfplumber
# from pdf2image import convert_from_path

# def extract_text_from_pdf(pdf_path):
#     text = ""
    
#     # Try extracting text using pdfplumber (for digital PDFs)
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             extracted_text = page.extract_text()
#             if extracted_text:  # If text is found, it's a digital PDF
#                 text += extracted_text + "\n"

#     # If no text was extracted, assume it's a scanned PDF and use OCR
#     if not text.strip():
#         print("No text found using pdfplumber, using OCR instead...")
#         images = convert_from_path(pdf_path)
#         for img in images:
#             text += pytesseract.image_to_string(img) + "\n"

#     return text

# pdf_path = "sample.pdf"
# pdf_text = extract_text_from_pdf(pdf_path)
# print("Extracted Text:\n", pdf_text)


# def extract_text_from_image(image_path):
#     """Extract text directly using Tesseract OCR without preprocessing."""
#     custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode 3, PSM 6 (Assumes a block of text)
#     img = Image.open(image_path)
#     text = pytesseract.image_to_string(img, config=custom_config)
#     return text

# print(extract_text_from_pdf("./sample.pdf"))

import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def extract_text(file_path):
    text = ""
    
    # Check if the file is a PDF
    if file_path.lower().endswith(".pdf"):
        # Try extracting text using pdfplumber (for digital PDFs)
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"

        # If no text was extracted, assume it's a scanned PDF and use OCR
        if not text.strip():
            images = convert_from_path(file_path)
            for img in images:
                text += pytesseract.image_to_string(img, config="--oem 3 --psm 6") + "\n"

    # If the file is an image (only .png, .jpeg, .jpg allowed)
    elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, config="--oem 3 --psm 6")

    else:
        raise ValueError("Unsupported file format. Only PDFs and PNG, JPEG, JPG images are allowed.")

    return text

