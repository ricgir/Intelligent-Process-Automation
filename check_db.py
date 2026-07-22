import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_system.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

print("Checking Database Connection...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")
        print("Successfully connected to PostgreSQL database!")
except Exception as e:
    print(f"PostgreSQL connection warning/error: {e}")
    print("Attempting migration commands...")

try:
    call_command('migrate')
    print("Migrations applied successfully!")
except Exception as e:
    print(f"Error during migration: {e}")
