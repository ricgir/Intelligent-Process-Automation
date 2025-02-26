import google.generativeai as genai
import json
import mimetypes


# Configure API Key
GOOGLE_API_KEY = "AIzaSyDXTVxlMMOWZiSKciSDH7dFjwx6X0ERYyg"
genai.configure(api_key=GOOGLE_API_KEY)


#Model Configuration
MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}


safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=MODEL_CONFIG,
    safety_settings=safety_settings,
)



def gemini_json_output(user_prompt):
    response = model.generate_content(user_prompt)
    return response.text


