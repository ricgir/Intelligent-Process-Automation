import os
import datetime
from decimal import Decimal, InvalidOperation
from django.db import transaction
from invoices.models import Invoice, InvoiceLineItem
from invoices.services.ocr_service import extract_text_from_file
from invoices.services.gemini_service import parse_invoice_text_with_gemini

def clean_decimal(value):
    if value is None or value == "":
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    try:
        cleaned = str(value).replace('$', '').replace('€', '').replace('£', '').replace(',', '').strip()
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None

def clean_date(value):
    if not value or not isinstance(value, str):
        return None
    cleaned = value.strip()
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y'):
        try:
            return datetime.datetime.strptime(cleaned, fmt).date()
        except ValueError:
            pass
    return None

def extract_invoice_data(file_path, original_filename=None):
    """
    Step 1: Runs OCR and Gemini AI parsing without saving to DB yet.
    Returns dictionary with extracted raw text and structured fields.
    """
    if not original_filename:
        original_filename = os.path.basename(file_path)

    extracted_text = extract_text_from_file(file_path)
    data = parse_invoice_text_with_gemini(extracted_text)
    data['original_filename'] = original_filename
    return data

def save_invoice_dict(data, original_filename=None):
    """
    Step 2: Saves verified dictionary (Header + Line Items) to DB inside an atomic transaction.
    Returns the created Invoice instance.
    """
    if not original_filename:
        original_filename = data.get('original_filename', 'invoice_document')

    invoice_number = data.get("invoice_number")
    if not invoice_number:
        invoice_number = f"INV-GEN-{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"

    if Invoice.objects.filter(invoice_number=invoice_number).exists():
        invoice_number = f"{invoice_number}-{datetime.datetime.now().strftime('%M%S')}"

    with transaction.atomic():
        invoice = Invoice.objects.create(
            invoice_number=str(invoice_number).strip(),
            invoice_date=clean_date(data.get("invoice_date")),
            due_date=clean_date(data.get("due_date")),
            vendor_name=data.get("vendor_name"),
            customer_name=data.get("customer_name"),
            subtotal=clean_decimal(data.get("subtotal")),
            taxes=clean_decimal(data.get("taxes")),
            total_amount=clean_decimal(data.get("total_amount")),
            payment_terms=data.get("payment_terms"),
            original_filename=original_filename,
            status='Success',
            raw_json=data
        )

        line_items_data = data.get("line_items", [])
        if isinstance(line_items_data, list):
            for item in line_items_data:
                if isinstance(item, dict):
                    InvoiceLineItem.objects.create(
                        invoice=invoice,
                        description=item.get("description"),
                        quantity=clean_decimal(item.get("quantity")),
                        unit_price=clean_decimal(item.get("unit_price")),
                        total=clean_decimal(item.get("total"))
                    )

    return invoice

def process_single_invoice_file(file_path, original_filename=None):
    """
    Convenience wrapper: Extracts OCR + Gemini AI and immediately saves to DB.
    """
    data = extract_invoice_data(file_path, original_filename=original_filename)
    return save_invoice_dict(data, original_filename=original_filename)
