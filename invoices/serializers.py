from rest_framework import serializers
from invoices.models import Invoice, InvoiceLineItem

class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total']


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_number',
            'invoice_date',
            'due_date',
            'vendor_name',
            'customer_name',
            'subtotal',
            'taxes',
            'total_amount',
            'payment_terms',
            'original_filename',
            'invoice_file',
            'status',
            'raw_json',
            'created_at',
            'updated_at',
            'line_items'
        ]


class InvoiceFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
