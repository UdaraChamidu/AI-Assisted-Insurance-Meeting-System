import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GEMINI_MODEL")

print(f"Testing Model: {model_name}")
print(f"API Key (last 4): ...{api_key[-4:] if api_key else 'None'}")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)

try:
    print("Attempting to generate content...")
    response = model.generate_content("Hello, this is a test.")
    print("Success! Response:", response.text)
except Exception as e:
    print("\nERROR DETECTED:")
    print(e)
