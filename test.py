import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:     
    print("❌ GEMINI_API_KEY not found in environment variables.")
    exit(1)

# Configure Gemini API
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content('Hi')
    print("✅ Gemini API Response:", response.text)
except Exception as e:
    print("❌ Error communicating with Gemini API:", e)
