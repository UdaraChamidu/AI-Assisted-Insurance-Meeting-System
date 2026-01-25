
import os
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("--- AI DIAGNOSTIC START ---")

# 1. Test Gemini
gemini_key = os.getenv("GOOGLE_API_KEY")
gemini_model = "gemini-1.5-flash" # Force a known valid model
print(f"\nTesting Gemini (Key starts with: {gemini_key[:5] if gemini_key else 'None'})...")
try:
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel(gemini_model)
    resp = model.generate_content("Hello")
    print(f"GEMINI SUCCESS. Response: {resp.text}")
except Exception as e:
    print(f"GEMINI FAILED: {e}")

# 2. Test OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
openai_model = "gpt-3.5-turbo"
print(f"\nTesting OpenAI (Key starts with: {openai_key[:5] if openai_key else 'None'})...")
try:
    client = OpenAI(api_key=openai_key)
    resp = client.chat.completions.create(
        model=openai_model,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(f"OPENAI SUCCESS. Response: {resp.choices[0].message.content}")
except Exception as e:
    print(f"OPENAI FAILED: {e}")

print("\n--- AI DIAGNOSTIC END ---")
