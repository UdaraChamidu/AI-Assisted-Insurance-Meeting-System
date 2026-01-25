
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GEMINI_MODEL")

print(f"API Key found: {'Yes' if api_key else 'No'} (starts with {api_key[:4] if api_key else 'None'})")
print(f"Model Name: {model_name}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    print("Attempting to generate content...")
    response = model.generate_content("Hello, are you working?")
    print("Success!")
    print("Response:", response.text)
except Exception as e:
    print("\nERROR DETAILS:")
    print(e)
