import json
import logging
from ocr_genai import gemini_json_output
from extract_text import extract_text_from_image
from database import insert_invoice

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Database Config
DB_CONFIG = {
    "dbname": "invoice_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def process_invoice(image_path):
    """
    Processes an invoice image:
    1. Extracts text using OCR.
    2. Converts extracted text to structured JSON using AI.
    3. Inserts structured JSON into PostgreSQL.
    """
    try:
        logging.info(f"Processing image: {image_path}")

        
        extracted_text = extract_text_from_image(image_path)
        if not extracted_text.strip():
            logging.error("OCR extraction failed or returned empty text.")
            return False  # Indicate failure

        
        user_prompt = f'''The following is the extracted text from an invoice:  

        "{extracted_text}"  

        Convert this extracted text into a structured JSON format, ensuring appropriate keys for:  
        - Invoice Number  
        - Invoice Date  
        - Due Date  
        - Vendor Name  
        - Customer Name  
        - Line Items (Description, Quantity, Unit Price, Total)  
        - Subtotal  
        - Taxes  
        - Total Amount  
        - Payment Terms  

        If any field is missing, return `null`. The JSON output should follow this structure:  

        {{
            "invoice_number": "value",
            "invoice_date": "YYYY-MM-DD",
            "due_date": "YYYY-MM-DD",
            "vendor_name": "value",
            "customer_name": "value",
            "line_items": [
                {{
                    "description": "value",
                    "quantity": "value",
                    "unit_price": "value",
                    "total": "value"
                }}
            ],
            "subtotal": "value",
            "taxes": "value",
            "total_amount": "value",
            "payment_terms": "value"
        }}

        Provide the JSON output directly, without any additional text or code blocks.
        '''

        logging.info("Sending text to AI model for JSON extraction...")
        invoice_json = gemini_json_output(user_prompt)

        
        if not invoice_json or invoice_json.strip() == "":
            logging.error("AI model returned an empty JSON string.")
            return False  

        try:
            
            if isinstance(invoice_json, dict):
                data = invoice_json
            else:
                data = json.loads(invoice_json)

            
            if not data:
                logging.error("AI model returned invalid JSON data.")
                return False

            
            insert_invoice(data, DB_CONFIG)
            logging.info("Invoice successfully inserted into the database.")
            return True  
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON response: {e}")
            return False  

    except Exception as e:
        logging.error(f"Error processing invoice: {e}")
        return False
