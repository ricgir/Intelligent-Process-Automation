from PIL import Image
import pytesseract
import argparse
import cv2
import os
import imutils


# img = Image.open('receipt_2.jpeg')

# text = pytesseract.image_to_string(img)

# print(text)
def extract_text_from_image(image_path):
    """Extract text directly using Tesseract OCR without preprocessing."""
    custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode 3, PSM 6 (Assumes a block of text)
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, config=custom_config)
    return text

print(extract_text_from_image("./invoice_4.png"))