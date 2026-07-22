import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_system.settings')
django.setup()

from invoices.services.invoice_processor import process_single_invoice_file

sample_path = os.path.abspath('invoice/invoices/sample.pdf')
if not os.path.exists(sample_path):
    print(f"Sample file not found at {sample_path}")
else:
    print(f"Testing invoice processing for: {sample_path}")
    try:
        invoice = process_single_invoice_file(sample_path, original_filename="sample.pdf")
        print(f"SUCCESS! Created Invoice ID={invoice.id}, Number={invoice.invoice_number}, Vendor={invoice.vendor_name}, Total={invoice.total_amount}")
        print(f"Line items count: {invoice.line_items.count()}")
    except Exception as e:
        print(f"ERROR processing invoice: {e}")
