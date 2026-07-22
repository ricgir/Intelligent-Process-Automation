from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from invoices.models import Invoice, InvoiceLineItem
from invoices.services.invoice_processor import clean_decimal, clean_date

class InvoiceModelTestCase(TestCase):
    def setUp(self):
        self.invoice = Invoice.objects.create(
            invoice_number="INV-1001",
            vendor_name="Acme Corp",
            customer_name="Global Tech",
            subtotal=Decimal("100.00"),
            taxes=Decimal("10.00"),
            total_amount=Decimal("110.00"),
            status="Success"
        )
        self.line_item = InvoiceLineItem.objects.create(
            invoice=self.invoice,
            description="Consulting Services",
            quantity=Decimal("2.00"),
            unit_price=Decimal("50.00"),
            total=Decimal("100.00")
        )

    def test_invoice_creation(self):
        """Test that an Invoice object is created with correct fields"""
        self.assertEqual(self.invoice.invoice_number, "INV-1001")
        self.assertEqual(self.invoice.total_amount, Decimal("110.00"))
        self.assertEqual(self.invoice.line_items.count(), 1)

    def test_line_item_relationship(self):
        """Test ForeignKey relationship between Invoice and InvoiceLineItem"""
        item = self.invoice.line_items.first()
        self.assertEqual(item.description, "Consulting Services")
        self.assertEqual(item.total, Decimal("100.00"))

    def test_clean_decimal_helper(self):
        """Test clean_decimal helper function with string formats"""
        self.assertEqual(clean_decimal("$1,234.56"), Decimal("1234.56"))
        self.assertEqual(clean_decimal("50.00"), Decimal("50.00"))
        self.assertIsNone(clean_decimal(None))
        self.assertIsNone(clean_decimal("invalid"))

    def test_clean_date_helper(self):
        """Test clean_date helper function with various date string formats"""
        d = clean_date("2025-01-15")
        self.assertIsNotNone(d)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 15)


class InvoiceAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.invoice = Invoice.objects.create(
            invoice_number="INV-2002",
            vendor_name="Widget Inc",
            total_amount=Decimal("250.00")
        )

    def test_get_invoices_list(self):
        """Test GET /api/invoices/ returns list of invoices"""
        response = self.client.get('/api/invoices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['invoice_number'], "INV-2002")

    def test_get_invoice_detail(self):
        """Test GET /api/invoices/{id}/ returns single invoice details"""
        response = self.client.get(f'/api/invoices/{self.invoice.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['invoice_number'], "INV-2002")
