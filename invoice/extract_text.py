import requests
import base64
import re
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import imutils

def extract_text_from_image(image_path):
    """Extract text directly using Tesseract OCR without preprocessing."""
    custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode 3, PSM 6 (Assumes a block of text)
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, config=custom_config)
    return text
