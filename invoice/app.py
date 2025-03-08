import os
#import shutil
#import tempfile
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from ocr_genai import gemini_json_output
from extract_text import extract_text
from database import insert_invoice
import json

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
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    
    if 'file' not in request.files and 'folder' not in request.files:
        flash('No file or folder selected')
        return redirect(request.url)
    
    processed_invoices = []
    uploaded_files = []
    
    # Single file upload
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_files.append(filepath)
    
    # Folder upload (multiple files)
    # elif 'folder' in request.files:
    #     files = request.files.getlist('folder')
    #     for file in files:
    #         if file.filename != '' and allowed_file(file.filename):
    #             filename = secure_filename(file.filename)
    #             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #             file.save(filepath)
    #             uploaded_files.append(filepath)
    
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
            
           
            if isinstance(invoice_json, dict):
                data = invoice_json
            else:
                data = json.loads(invoice_json)
            
           
            insert_invoice(data, DB_CONFIG)
            
            
            processed_result = {
                'filename': os.path.basename(filepath),
                'json_data': data,
                'status': 'Success'
            }
            processed_invoices.append(processed_result)
            
        except Exception as e:
            
            processed_result = {
                'filename': os.path.basename(filepath),
                'json_data': None,
                'status': f'Error: {str(e)}'
            }
            processed_invoices.append(processed_result)
    
   
    session['processed_invoices'] = processed_invoices
    
   
    for filepath in uploaded_files:
        if os.path.exists(filepath):
            os.remove(filepath)
    
    return redirect(url_for('results'))

@app.route('/results')
def results():
    processed_invoices = session.get('processed_invoices', [])
    if not processed_invoices:
        flash('No invoices were processed. Please upload files first.')
        return redirect(url_for('index'))
    
    return render_template('results.html', invoices=processed_invoices)

if __name__ == '__main__':
    app.run(debug=True)

# import os
# import json
# import uuid
# from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
# from werkzeug.utils import secure_filename
# from ocr_genai import gemini_json_output
# from extract_text import extract_text
# from database import insert_invoice

# app = Flask(__name__)
# app.secret_key = "invoice_processor_secret_key"

# # Create a temporary folder for uploads that will be cleared when the app exits
# UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_uploads')
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# DB_CONFIG = {
#     "dbname": "invoice_db",
#     "user": "postgres",
#     "password": "postgres",
#     "host": "localhost",
#     "port": "5432"
# }

# # Ensure upload folder exists
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/', methods=['GET'])
# def index():
#     if 'processed_invoices' in session:
#         session.pop('processed_invoices')
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     processed_invoices = []
#     uploaded_files = []
    
#     # Handle different types of file input names from both form versions
#     file_inputs = ['file', 'files']
#     all_files = []
    
#     for input_name in file_inputs:
#         if input_name in request.files:
#             files = request.files.getlist(input_name)
#             if files and any(file.filename != '' for file in files):
#                 all_files.extend([f for f in files if f.filename != ''])
    
#     if not all_files:
#         flash('No files selected')
#         return redirect(url_for('index'))
    
#     # Process each valid file
#     for file in all_files:
#         if file and allowed_file(file.filename):
#             original_filename = file.filename
#             # Generate a unique filename to avoid collisions
#             extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
#             unique_filename = f"{str(uuid.uuid4())}.{extension}" if extension else str(uuid.uuid4())
            
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
#             file.save(filepath)
            
#             # Store both the unique path and original filename
#             uploaded_files.append({
#                 'path': filepath,
#                 'original_name': original_filename
#             })
    
#     # Process all uploaded files
#     for file_info in uploaded_files:
#         try:
#             filepath = file_info['path']
#             original_filename = file_info['original_name']
            
#             extracted_text = extract_text(filepath)
#             user_prompt = f'''The following is the extracted text from an invoice:
# "{extracted_text}"
# Convert this extracted text into a structured JSON format, ensuring appropriate keys for:
# - Invoice Number
# - Invoice Date
# - Due Date
# - Vendor Name
# - Customer Name
# - Line Items (Description, Quantity, Unit Price, Total)
# - Subtotal
# - Taxes
# - Total Amount
# - Payment Terms
# If any field is missing, return `null`. The JSON output should follow this structure:
# {{
# "invoice_number": "value",
# "invoice_date": "YYYY-MM-DD",
# "due_date": "YYYY-MM-DD",
# "vendor_name": "value",
# "customer_name": "value",
# "line_items": [
#   {{
#     "description": "value",
#     "quantity": "value",
#     "unit_price": "value",
#     "total": "value"
#   }}
# ],
# "subtotal": "value",
# "taxes": "value",
# "total_amount": "value",
# "payment_terms": "value"
# }}
# Provide the JSON output directly, without any additional text or code blocks.
# '''
#             invoice_json = gemini_json_output(user_prompt)
#             data = json.loads(invoice_json) if isinstance(invoice_json, str) else invoice_json
#             insert_invoice(data, DB_CONFIG)
            
#             processed_result = {
#                 'filename': original_filename,
#                 'json_data': data,
#                 'status': 'Success'
#             }
#             processed_invoices.append(processed_result)
#         except Exception as e:
#             processed_result = {
#                 'filename': original_filename,
#                 'json_data': None,
#                 'status': f'Error: {str(e)}'
#             }
#             processed_invoices.append(processed_result)
    
#     # Store results in session for the results page
#     session['processed_invoices'] = processed_invoices
    
#     # Clean up temporary files immediately after processing
#     for file_info in uploaded_files:
#         filepath = file_info['path']
#         if os.path.exists(filepath):
#             os.remove(filepath)
    
#     return redirect(url_for('results'))

# @app.route('/results')
# def results():
#     processed_invoices = session.get('processed_invoices', [])
#     if not processed_invoices:
#         flash('No invoices were processed. Please upload files first.')
#         return redirect(url_for('index'))
    
#     return render_template('results.html', invoices=processed_invoices)

# # Function to clean up temp files when the app starts (in case of previous crash)
# def cleanup_temp_files():
#     for filename in os.listdir(UPLOAD_FOLDER):
#         file_path = os.path.join(UPLOAD_FOLDER, filename)
#         try:
#             if os.path.isfile(file_path):
#                 os.remove(file_path)
#         except Exception as e:
#             print(f"Error deleting {file_path}: {e}")

# if __name__ == '__main__':
#     # Clean up any leftover files from previous runs
#     cleanup_temp_files()
    
#     # Register function to clean up files when app exits
#     import atexit
#     atexit.register(cleanup_temp_files)
    
#     app.run(debug=True)