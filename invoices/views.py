import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from invoices.models import Invoice
from invoices.serializers import InvoiceSerializer
from invoices.services.invoice_processor import (
    process_single_invoice_file,
    extract_invoice_data,
    save_invoice_dict
)

# --- DRF REST API ViewSet ---
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-created_at')
    serializer_class = InvoiceSerializer

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def extract(self, request):
        """
        POST /api/invoices/extract/
        Runs OCR & Gemini AI extraction on uploaded file.
        Saves file to S3/default_storage permanently.
        Returns extracted data preview WITHOUT saving DB metadata yet.
        """
        file_obj = request.FILES.get('file') or request.FILES.get('files')
        if not file_obj:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        fs = FileSystemStorage(location=temp_dir)
        saved_name = fs.save(file_obj.name, file_obj)
        saved_path = fs.path(saved_name)

        try:
            # 1. OCR + AI extraction locally
            extracted_data = extract_invoice_data(saved_path, original_filename=file_obj.name)
            
            # 2. Persist file permanently to S3/default_storage
            from django.core.files.storage import default_storage
            with open(saved_path, 'rb') as f:
                perm_saved_name = default_storage.save(f"invoices/{file_obj.name}", f)
            
            # Add permanent URL/path reference to the data dict
            extracted_data['invoice_file'] = perm_saved_name
            
            return Response({
                'success': True,
                'extracted_data': extracted_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            if os.path.exists(saved_path):
                os.remove(saved_path)

    @action(detail=False, methods=['post'], parser_classes=[JSONParser, FormParser])
    def confirm(self, request):
        """
        POST /api/invoices/confirm/
        Accepts verified JSON payload (header + line items + invoice_file path) and persists to Database.
        """
        data = request.data
        if not data:
            return Response({'error': 'No invoice payload provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = save_invoice_dict(data, original_filename=data.get('original_filename'))
            return Response({
                'success': True,
                'message': 'Invoice successfully accepted and saved to database!',
                'invoice': InvoiceSerializer(invoice).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """
        POST /api/invoices/upload/
        Immediate direct upload and save action.
        """
        files = request.FILES.getlist('file') or request.FILES.getlist('files')
        if not files:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        fs = FileSystemStorage(location=temp_dir)

        results = []
        errors = []

        for file_obj in files:
            saved_name = fs.save(file_obj.name, file_obj)
            saved_path = fs.path(saved_name)
            try:
                # 1. OCR + AI extraction locally
                data = extract_invoice_data(saved_path, original_filename=file_obj.name)
                
                # 2. Persist file permanently to S3/default_storage
                from django.core.files.storage import default_storage
                with open(saved_path, 'rb') as f:
                    perm_saved_name = default_storage.save(f"invoices/{file_obj.name}", f)
                data['invoice_file'] = perm_saved_name
                
                # 3. Save DB models
                invoice = save_invoice_dict(data, original_filename=file_obj.name)
                results.append(InvoiceSerializer(invoice).data)
            except Exception as e:
                errors.append({'filename': file_obj.name, 'error': str(e)})
            finally:
                if os.path.exists(saved_path):
                    os.remove(saved_path)

        return Response({
            'processed': results,
            'errors': errors,
            'total_processed': len(results),
            'total_errors': len(errors)
        }, status=status.HTTP_201_CREATED if results else status.HTTP_400_BAD_REQUEST)


# --- HTML Template Web Views ---
def index_view(request):
    invoices = Invoice.objects.all().order_by('-created_at')[:10]
    return render(request, 'index.html', {'invoices': invoices})


def results_view(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    return render(request, 'results.html', {'invoices': invoices})
