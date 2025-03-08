import os
import json
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from ocr_genai import gemini_json_output
from extract_text import extract_text
from database import insert_invoice

app = Flask(__name__)
app.secret_key = "invoice_processor_secret_key"  

UPLOAD_FOLDER = "temp_uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
DB_CONFIG = {
    "dbname": "invoice_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'processed_invoices' in session:
        session.pop('processed_invoices')
    
    # Get list of files currently in the temp folder
    temp_files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename):
            temp_files.append(filename)
    
    return render_template('index.html', temp_files=temp_files)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash(f'File {filename} uploaded successfully', 'success')
    else:
        flash('Invalid file type. Please upload PNG, JPG, JPEG, or PDF files.', 'error')
    
    return redirect(url_for('index'))

@app.route('/process_invoices', methods=['POST'])
def process_invoices():
    # Get all files from the temp folder
    uploaded_files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_files.append(filepath)
    
    if not uploaded_files:
        flash('No files to process. Please upload files first.')
        return redirect(url_for('index'))
    
    processed_invoices = []
    
    # Process each uploaded file
    for filepath in uploaded_files:
        try:
            extracted_text = extract_text(filepath)
            
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
"invoice_number": "value",
"invoice_date": "YYYY-MM-DD",
"due_date": "YYYY-MM-DD",
"vendor_name": "value",
"customer_name": "value",
"line_items": [
"description": "value",
"quantity": "value",
"unit_price": "value",
"total": "value"
],
"subtotal": "value",
"taxes": "value",
"total_amount": "value",
"payment_terms": "value"
Provide the JSON output directly, without any additional text or code blocks.
'''
            invoice_json = gemini_json_output(user_prompt)
            print(invoice_json)
            if not invoice_json:  # Check if JSON output is empty
                raise ValueError("Data extraction failed. No JSON output received.")

            if isinstance(invoice_json, dict):
                data = invoice_json
            else:
                try:
                    data = json.loads(invoice_json)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format received.")

            if not data.get("invoice_number"):  # Check if invoice_number is missing
                raise ValueError("Invoice number not found in extracted data.")

            insert_result = insert_invoice(data, DB_CONFIG)

            if insert_result != "Success":  # If insert_invoice() returns an error
                raise ValueError(f"Database error: {insert_result}")

            processed_result = {
                'filename': os.path.basename(filepath),
                'json_data': data,
                'status': 'Success'
            }
            processed_invoices.append(processed_result)

        except ValueError as ve:
            processed_result = {
                'filename': os.path.basename(filepath),
                'json_data': None,
                'status': f'Error: {str(ve)}'
            }
            processed_invoices.append(processed_result)

        except Exception as e:
            processed_result = {
                'filename': os.path.basename(filepath),
                'json_data': None,
                'status': f'Unexpected Error: {str(e)}'
            }
            processed_invoices.append(processed_result)
    
    # Store processing results in session
    session['processed_invoices'] = processed_invoices
    
    # Clean up the temp folder after processing
    for filepath in uploaded_files:
        if os.path.exists(filepath):
            os.remove(filepath)
    
    return redirect(url_for('results'))

@app.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    # Clear all files from the temp folder
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
    
    flash('All uploaded files have been cleared', 'success')
    return redirect(url_for('index'))

@app.route('/results')
def results():
    processed_invoices = session.get('processed_invoices', [])
    if not processed_invoices:
        flash('No invoices were processed. Please upload files first.')
        return redirect(url_for('index'))
    
    return render_template('results.html', invoices=processed_invoices)

if __name__ == '__main__':
    app.run(debug=True)

