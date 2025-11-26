import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key found: {bool(api_key)}")
print(f"API Key length: {len(api_key) if api_key else 0}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        print("API configured successfully")

        # List available models
        print("\nAvailable models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")

        # Test with vision-capable model
        print("\nTesting vision capabilities...")
        model_names = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'gemini-2.0-flash-exp'
        ]

        for model_name in model_names:
            try:
                print(f"\nTrying model: {model_name}")
                model = genai.GenerativeModel(model_name)

                # Test with text first
                response = model.generate_content("Hello, this is a test.")
                print(f"SUCCESS {model_name}: {response.text[:100]}...")
                break

            except Exception as e:
                print(f"FAILED {model_name}: {str(e)}")

    except Exception as e:
        print(f"API configuration failed: {str(e)}")
else:
    print("No API key found")