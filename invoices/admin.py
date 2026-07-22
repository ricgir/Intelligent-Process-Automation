from django.contrib import admin
from invoices.models import Invoice, InvoiceLineItem

class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0
    fields = ('description', 'quantity', 'unit_price', 'total')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'vendor_name',
        'customer_name',
        'total_amount',
        'invoice_date',
        'created_at'
    )
    search_fields = ('invoice_number', 'vendor_name', 'customer_name', 'original_filename')
    list_filter = ('invoice_date', 'vendor_name', 'status', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'raw_json')
    inlines = [InvoiceLineItemInline]

@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'description', 'quantity', 'unit_price', 'total')
    search_fields = ('description', 'invoice__invoice_number')
