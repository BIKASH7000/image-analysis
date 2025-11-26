"""
Test script to verify the image analyzer setup
"""

import sys
import os

def check_imports():
    """Check if all required packages can be imported"""
    print("Checking imports...")

    try:
        import streamlit as st
        print("✓ Streamlit imported successfully")
    except ImportError:
        print("✗ Streamlit import failed. Install with: pip install streamlit")
        return False

    try:
        import google.generativeai as genai
        print("✓ Google Generative AI imported successfully")
    except ImportError:
        print("✗ Google Generative AI import failed. Install with: pip install google-generativeai")
        return False

    try:
        from PIL import Image
        print("✓ PIL (Pillow) imported successfully")
    except ImportError:
        print("✗ PIL import failed. Install with: pip install pillow")
        return False

    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv imported successfully")
    except ImportError:
        print("✗ python-dotenv import failed. Install with: pip install python-dotenv")
        return False

    return True

def check_env_file():
    """Check if .env file exists and has the required API key"""
    print("\nChecking environment setup...")

    if os.path.exists('.env'):
        print("✓ .env file exists")

        # Load and check the .env file
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key and api_key != 'your_google_api_key_here':
            print("✓ Google API key is configured")
            return True
        else:
            print("✗ Google API key is not set or is using placeholder value")
            print("  Please edit .env file and add your actual API key")
            return False
    else:
        print("✗ .env file not found")
        print("  Copy .env.example to .env and add your Google API key")
        return False

def main():
    """Run all setup checks"""
    print("Image Analyzer Setup Test")
    print("=" * 30)

    imports_ok = check_imports()
    env_ok = check_env_file()

    print("\n" + "=" * 30)

    if imports_ok and env_ok:
        print("✓ All checks passed! You're ready to run the app.")
        print("\nTo start the application:")
        print("streamlit run app.py")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nTo install missing packages:")
        print("pip install -r requirements.txt")

        if not env_ok:
            print("\nTo set up environment:")
            print("1. Copy .env.example to .env")
            print("2. Edit .env and add your Google API key")
            print("   Get an API key from: https://makersuite.google.com/app/apikey")

    return imports_ok and env_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)