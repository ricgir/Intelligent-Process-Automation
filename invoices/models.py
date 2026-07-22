from django.db import models

class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100, unique=True, db_index=True)
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    vendor_name = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    taxes = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_terms = models.CharField(max_length=255, null=True, blank=True)
    
    original_filename = models.CharField(max_length=255, null=True, blank=True)
    invoice_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    status = models.CharField(max_length=50, default='Success')
    raw_json = models.JSONField(null=True, blank=True, help_text="Full raw JSON from AI extraction")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.vendor_name or 'Unknown Vendor'}"


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='line_items', on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"LineItem ({self.description or 'No desc'}) - Total: {self.total}"
