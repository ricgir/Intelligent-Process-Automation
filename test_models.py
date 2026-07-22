import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_system.settings')
django.setup()

import google.generativeai as genai
from django.conf import settings

api_key = settings.GEMINI_API_KEY
print(f"Testing API Key: '{api_key[:8]}...' (Length: {len(api_key)})")

genai.configure(api_key=api_key)

try:
    print("\n--- Listing Available Models via genai.list_models() ---")
    models = list(genai.list_models())
    found_any = False
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"Supported Model: {m.name}")
            found_any = True
    if not found_any:
        print("No models found that support generateContent.")
except Exception as e:
    print(f"Error listing models: {type(e).__name__} - {e}")
