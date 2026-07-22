import json
import google.generativeai as genai
from django.conf import settings

def parse_invoice_text_with_gemini(extracted_text):
    """
    Sends extracted OCR text to Gemini AI and retrieves structured invoice JSON.
    Dynamically discovers available models for the configured API key.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not configured.")

    genai.configure(api_key=api_key)

    # Dynamically query available models for this API Key
    candidate_models = []
    try:
        available_models = list(genai.list_models())
        for m in available_models:
            if 'generateContent' in getattr(m, 'supported_generation_methods', []):
                name = m.name.replace('models/', '')
                candidate_models.append(name)
    except Exception:
        pass

    # Fallback default model candidates if dynamic listing fails or is restricted
    if not candidate_models:
        candidate_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-flash"]

    # Sort to prioritize 'flash' models for fast inference
    candidate_models.sort(key=lambda x: 0 if 'flash' in x else 1)

    model_config = {
        "temperature": 0.1,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 4096,
        "response_mime_type": "application/json",
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    prompt = f'''The following is extracted text from an invoice:
"{extracted_text}"

Extract and convert this text into a JSON object adhering to the following key structure:
{{
  "invoice_number": "string",
  "invoice_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "vendor_name": "string",
  "customer_name": "string",
  "subtotal": 0.00,
  "taxes": 0.00,
  "total_amount": 0.00,
  "payment_terms": "string",
  "line_items": [
    {{
      "description": "string",
      "quantity": 0.00,
      "unit_price": 0.00,
      "total": 0.00
    }}
  ]
}}
If any field is missing or cannot be inferred, set its value to null.
Ensure numerical values for subtotal, taxes, total_amount, quantity, unit_price, and total are numeric or null.
Respond ONLY with valid JSON.
'''

    response = None
    last_error = None

    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=model_config,
                safety_settings=safety_settings,
            )
            res = model.generate_content(prompt)
            if res and res.text:
                response = res
                break
        except Exception as err:
            last_error = err

    if not response or not response.text:
        raise ValueError(f"Gemini API call failed across models {candidate_models[:5]}. Last error: {last_error}")

    try:
        data = json.loads(response.text)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response from Gemini API: {str(e)}")
