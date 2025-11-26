import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("Available models:")
try:
    models = genai.list_models()
    for model in models:
        print(f"- {model.name}: {model.display_name}")
        print(f"  Supported generation methods: {model.supported_generation_methods}")
        print()
except Exception as e:
    print(f"Error listing models: {e}")