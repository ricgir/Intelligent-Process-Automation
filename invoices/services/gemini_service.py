import json
import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Known working models for this API key (in priority order)
# Updated: gemini-1.5-flash/pro deprecated — use gemini-flash-latest as primary fallback
FALLBACK_MODELS = [
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
]

def parse_invoice_text_with_gemini(extracted_text):
    """
    Sends extracted OCR text to Gemini AI and retrieves structured invoice JSON.
    Dynamically discovers available models for the configured API key,
    falling back to FALLBACK_MODELS if dynamic listing fails.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Set it as an environment variable in your Render dashboard under Environment settings."
        )

    genai.configure(api_key=api_key)

    # Dynamically query available models for this API Key
    candidate_models = []
    try:
        available_models = list(genai.list_models())
        for m in available_models:
            if 'generateContent' in getattr(m, 'supported_generation_methods', []):
                name = m.name.replace('models/', '')
                candidate_models.append(name)
        logger.info(f"Gemini: discovered {len(candidate_models)} available models.")
    except Exception as e:
        logger.warning(f"Gemini: could not list models dynamically ({e}). Using fallback list.")

    # Use fallback if dynamic listing returned nothing
    if not candidate_models:
        candidate_models = FALLBACK_MODELS
        logger.info(f"Gemini: using fallback model list: {candidate_models}")

    # Prioritise 'flash' models for speed
    candidate_models.sort(key=lambda x: 0 if 'flash' in x.lower() else 1)

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
            logger.info(f"Gemini: trying model '{model_name}'...")
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=model_config,
                safety_settings=safety_settings,
            )
            res = model.generate_content(prompt)
            if res and res.text:
                logger.info(f"Gemini: success with model '{model_name}'.")
                response = res
                break
        except Exception as err:
            logger.warning(f"Gemini: model '{model_name}' failed — {err}")
            last_error = err

    if not response or not response.text:
        raise ValueError(
            f"Gemini API call failed across all tried models. Last error: {last_error}. "
            f"Ensure GEMINI_API_KEY is set in Render Environment Variables."
        )

    try:
        data = json.loads(response.text)
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response from Gemini API: {str(e)}")

