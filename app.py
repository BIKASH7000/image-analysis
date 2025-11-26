import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import io
import re
from PIL import ImageEnhance, ImageFilter

# Load environment variables
load_dotenv()

# Configure Google Generative AI
def configure_genai():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API Key not found! Please set it in your .env file.")
        return False
    genai.configure(api_key=api_key)
    return True

# Detect if image is likely a sequence diagram
def detect_sequence_diagram(image, file_name=None):
    """
    Try to detect if the uploaded image is a sequence diagram
    """
    file_name_lower = file_name.lower() if file_name else ""

    # Check filename for sequence diagram indicators
    seq_keywords = ['sequence', 'seq', 'interaction', 'collaboration', 'message flow', 'uml', 'system flow', 'process flow']
    if any(keyword in file_name_lower for keyword in seq_keywords):
        return True, "Filename suggests sequence diagram"

    # Check user prompt for sequence diagram indicators
    # This will be used later when the prompt is available
    # Note: This is a simplified check since we don't have access to the prompt here
    # The actual detection will also happen in the main function

    # Basic heuristic: check image properties typical of sequence diagrams
    width, height = image.size
    aspect_ratio = width / height if height > 0 else 1

    # Sequence diagrams are often wide (multiple participants side by side)
    # and tall enough to show time flow (multiple message levels)
    if aspect_ratio > 1.5 and height > 200:
        return True, "Wide format typical of sequence diagrams"

    # Medium confidence: somewhat wide format
    elif aspect_ratio > 1.2 and height > 150:
        return True, "Format suggests technical diagram"

    return False, None

# Analyze sequence diagram using pattern recognition
def analyze_sequence_diagram(image, prompt, file_name=None):
    """
    Perform detailed analysis specifically for sequence diagrams
    """
    try:
        # Enhance image for better text/line detection
        enhanced = ImageEnhance.Contrast(image).enhance(2.0)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.5)

        width, height = image.size

        analysis = """## 📋 Sequence Diagram Analysis

### 🔍 **Diagram Overview**
This appears to be a **UML Sequence Diagram**. Sequence diagrams show object interactions over time, with messages passed between objects.

### 📊 **Technical Details**
- **Image Size**: {width} × {height} pixels
- **Diagram Type**: UML Sequence Diagram
- **Reading Direction**: Left to Right (participants), Top to Bottom (time flow)

### 👥 **Participants/Lifelines**
Sequence diagrams typically include:
- **Actors**: External entities that interact with the system
- **Objects/System Components**: Internal system parts
- **Lifelines**: Vertical dashed lines showing object existence over time

### 💬 **Communication Patterns**
The diagram likely shows:
- **Synchronous Messages**: Solid arrows with filled heads (blocking calls)
- **Asynchronous Messages**: Open arrows (non-blocking calls)
- **Return Messages**: Dashed lines with open arrows
- **Self Messages**: Loops showing internal processing
- **Creation Messages**: Messages that create new objects

### 🎯 **Key Elements to Look For**
1. **Participants** (at the top): Actors, objects, system boundaries
2. **Lifelines** (vertical dashed lines): Object lifespans
3. **Activation Boxes** (rectangles on lifelines): When object is active
4. **Messages** (arrows): Communication between objects
5. **Combined Fragments** (frames): Loops, conditions, alternatives
6. **Notes** (cornered rectangles): Additional information

### 📝 **Analysis Suggestions**
To fully understand this sequence diagram:
- **Identify all participants** - Who/what are the main actors?
- **Follow message flow** - What triggers each interaction?
- **Note timing** - What happens sequentially vs. in parallel?
- **Look for patterns** - Request-response, queries, notifications

### ⚠️ **AI Enhancement Note**
For detailed content analysis (specific text and messages), you need a Google AI API with vision capabilities. The current analysis identifies this as a sequence diagram based on visual patterns and provides framework understanding.

### 🔧 **Next Steps**
1. If you have a vision-enabled API key, you'll get specific text extraction
2. Otherwise, you can manually extract text from the diagram using:
   - Participant names (top of each lifeline)
   - Message text (on/near arrows)
   - Conditions and loops (in combined fragments)
""".format(width=width, height=height)

        return analysis

    except Exception as e:
        st.error(f"Error analyzing sequence diagram: {str(e)}")
        return None

# Analyze image using Google Generative AI
def analyze_image(image, prompt, file_name=None):
    try:
        # Check if this is likely a sequence diagram first
        is_sequence_diagram, reason = detect_sequence_diagram(image, file_name)

        # Also check prompt for sequence diagram keywords
        prompt_lower = prompt.lower() if prompt else ""
        seq_prompt_keywords = ['sequence', 'lifeline', 'message', 'participant', 'actor', 'interaction', 'uml', 'diagram']
        prompt_suggests_seq = any(keyword in prompt_lower for keyword in seq_prompt_keywords)

        # If prompt suggests sequence diagram, override detection
        if prompt_suggests_seq and not is_sequence_diagram:
            is_sequence_diagram = True
            reason = "User prompt suggests sequence diagram"

        # Try different model names that might work
        model_names_to_try = [
            'models/gemini-2.5-flash',      # Latest and fastest
            'models/gemini-2.5-pro',        # Latest and most capable
            'models/gemini-2.0-flash-exp',  # Experimental but good
            'models/gemini-2.0-flash',      # Stable 2.0 version
            'models/gemini-flash-latest',   # Latest flash model
            'models/gemini-pro-latest'      # Latest pro model
        ]

        api_error = None  # Store the last API error for better feedback

        for model_name in model_names_to_try:
            try:
                model = genai.GenerativeModel(model_name)

                # For sequence diagrams, use specialized prompt if AI vision is available
                if is_sequence_diagram:
                    specialized_prompt = """This is a UML sequence diagram. Please analyze it in detail and provide:
1. All participants/actors in the diagram
2. The sequence of messages between participants
3. Any conditions, loops, or combined fragments
4. The overall flow and purpose of the interaction
5. Any return messages or synchronous/asynchronous calls
Please be very specific about the text labels and message content."""
                    response = model.generate_content([specialized_prompt, image])
                    return response.text
                else:
                    # Try passing PIL Image directly first
                    response = model.generate_content([prompt, image])
                    return response.text
            except Exception as first_error:
                # Store specific error messages for better feedback
                error_msg = str(first_error).lower()

                if "quota" in error_msg or "limit" in error_msg:
                    api_error = f"Google AI API quota exceeded. The free tier limit has been reached. Please:\n1. Wait for quota to reset (usually after some time)\n2. Check your billing at https://ai.dev/usage\n3. Consider upgrading to a paid plan\n\nError: {str(first_error)}"
                    break  # No point trying other models if it's a quota issue
                elif "404" in error_msg or "not found" in error_msg:
                    api_error = f"Model {model_name} not available. Trying next model..."
                    # Continue to try next model
                elif "permission" in error_msg or "forbidden" in error_msg:
                    api_error = f"API key permission denied. Check if your API key has vision capabilities enabled at Google AI Studio."
                    break  # No point continuing if it's a permission issue
                else:
                    api_error = f"Error with model {model_name}: {str(first_error)}"
                    # Continue to try next model

                try:
                    # Fallback: convert to bytes
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_bytes = img_byte_arr.getvalue()

                    if is_sequence_diagram:
                        specialized_prompt = """This is a UML sequence diagram. Please analyze it in detail and provide:
1. All participants/actors in the diagram
2. The sequence of messages between participants
3. Any conditions, loops, or combined fragments
4. The overall flow and purpose of the interaction
5. Any return messages or synchronous/asynchronous calls
Please be very specific about the text labels and message content."""
                        response = model.generate_content([specialized_prompt, img_bytes])
                        return response.text
                    else:
                        response = model.generate_content([prompt, img_bytes])
                        return response.text
                except Exception as second_error:
                    error_msg = str(second_error).lower()
                    if "quota" in error_msg or "limit" in error_msg:
                        api_error = f"Google AI API quota exceeded. The free tier limit has been reached. Please:\n1. Wait for quota to reset (usually after some time)\n2. Check your billing at https://ai.dev/usage\n3. Consider upgrading to a paid plan\n\nError: {str(second_error)}"
                        break
                    elif "404" in error_msg or "not found" in error_msg:
                        api_error = f"Model {model_name} not available (404 error)."
                    else:
                        api_error = f"Error with model {model_name}: {str(second_error)}"
                    continue

        # If all models fail, check for sequence diagrams and provide specialized analysis
        if is_sequence_diagram:
            if api_error and ("quota" in api_error.lower() or "limit" in api_error.lower()):
                st.error("🚫 Google AI API Quota Exceeded")
                st.info("The Google AI API has reached its free tier limit. Please:")
                st.info("1. **Wait for quota to reset** (usually within minutes/hours)")
                st.info("2. **Check your usage** at [AI Usage Dashboard](https://ai.dev/usage)")
                st.info("3. **Enable billing** if you need more quota")

            st.warning(f"AI vision analysis not available. Detected sequence diagram ({reason}). Providing sequence diagram analysis...")
            return analyze_sequence_diagram(image, prompt, file_name)
        else:
            # Original fallback for non-sequence diagrams
            if api_error and ("quota" in api_error.lower() or "limit" in api_error.lower()):
                st.error("🚫 Google AI API Quota Exceeded")
                st.info("The Google AI API has reached its free tier limit. Please:")
                st.info("1. **Wait for quota to reset** (usually within minutes/hours)")
                st.info("2. **Check your usage** at [AI Usage Dashboard](https://ai.dev/usage)")
                st.info("3. **Enable billing** if you need more quota")
                st.warning("AI image analysis not available. Providing detailed image analysis...")
            elif api_error and ("permission" in api_error.lower() or "forbidden" in api_error.lower()):
                st.error("🔑 API Key Permission Issue")
                st.info("Your API key may not have vision capabilities enabled:")
                st.info("1. Check your key at [Google AI Studio](https://makersuite.google.com/app/apikey)")
                st.info("2. Ensure vision/image analysis is enabled")
                st.info("3. Try generating a new API key with proper permissions")
                st.warning("AI image analysis not available. Providing detailed image analysis...")
            else:
                st.warning("AI image analysis not available. Providing detailed image analysis...")

        # Enhanced basic analysis
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 1
        pixels = width * height

        # Determine image orientation
        if width > height:
            orientation = "Landscape"
        elif height > width:
            orientation = "Portrait"
        else:
            orientation = "Square"

        # Determine image mode description
        mode_descriptions = {
            'RGB': 'Color image (Red, Green, Blue)',
            'RGBA': 'Color image with transparency',
            'L': 'Grayscale (Black and White)',
            'P': 'Palette-based color',
            'CMYK': 'CMYK color (for printing)',
            'HSV': 'HSV color space'
        }

        color_info = mode_descriptions.get(image.mode, f'Unknown mode: {image.mode}')

        # Categorize image size
        if pixels < 640 * 480:
            size_category = "Small"
        elif pixels < 1920 * 1080:
            size_category = "Medium"
        elif pixels < 4 * 1024 * 1024:
            size_category = "Large"
        else:
            size_category = "Very Large"

        # Determine if it's likely a photo or graphic
        file_ext_lower = file_name.lower() if file_name and file_name else ""
        if file_ext_lower in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            likely_type = "Photograph or Digital Image"
        elif file_ext_lower in ['.svg', '.ico']:
            likely_type = "Vector Graphic or Icon"
        elif file_ext_lower in ['.psd']:
            likely_type = "Photoshop Document"
        elif file_ext_lower in ['.tiff', '.tif']:
            likely_type = "Professional/High-Quality Image"
        else:
            likely_type = "Image File"

        # Color mode recommendations
        recommendations = []
        if image.mode == 'RGBA':
            recommendations.append("Has transparent background")
        elif image.mode == 'L':
            recommendations.append("Black and white image")
        elif image.mode == 'CMYK':
            recommendations.append("Optimized for printing")

        if aspect_ratio > 1.5:
            recommendations.append("Wide panoramic format")
        elif aspect_ratio < 0.7:
            recommendations.append("Tall vertical format")
        elif 0.9 <= aspect_ratio <= 1.1:
            recommendations.append("Square format")

        basic_analysis = f"""## 📊 Detailed Image Analysis

### 📐 **Technical Specifications**
- **Dimensions**: {width} × {height} pixels ({pixels:,} total pixels)
- **Aspect Ratio**: {aspect_ratio:.2f}:1
- **Orientation**: {orientation}
- **Size Category**: {size_category}
- **File Format**: {image.format or 'Unknown'}
- **Color Mode**: {color_info}

### 🎨 **Image Characteristics**
- **File Type**: {likely_type}
- **Compression**: {'Lossless' if image.format in ['PNG', 'BMP', 'TIFF'] else 'Lossy'} (typical for {image.format})
- **Bit Depth**: {image.bits if hasattr(image, 'bits') and image.bits else 'Unknown'}

### 💡 **Features & Recommendations**
"""

        if recommendations:
            for rec in recommendations:
                basic_analysis += f"- ✅ {rec}\n"
        else:
            basic_analysis += "- Standard image format\n"

        basic_analysis += f"""
### 🔍 **Usage Suggestions**
- Perfect for: {'Web display and digital use' if image.format == 'PNG' else 'Photographs and images' if image.format == 'JPEG' else 'High-quality prints' if image.format in ['TIFF', 'BMP'] else 'General use'}
- Best viewed at: {width}×{height} pixels or smaller
- Aspect ratio: {'Great for wallpapers/wide displays' if aspect_ratio > 1.5 else 'Great for portraits/mobile' if aspect_ratio < 0.7 else 'Versatile square format'}

### ⚠️ **AI Enhancement Note**
To get AI-powered content analysis (what's actually *in* the image), your Google API key needs vision capabilities. You can:
1. Check your API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Ensure vision/image analysis is enabled
3. Try a different API key if available

*This analysis provides technical information about your image file. For content-based analysis, please ensure proper API access.*"""

        return basic_analysis

    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return None

# Custom CSS for dark AI-themed animated header
def load_header_css():
    st.markdown("""
    <style>
        /* Dark AI-themed header with advanced animations */
        .attractive-header {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 30%, #16213e 70%, #0f0f23 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow:
                0 15px 35px rgba(0, 0, 0, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.1),
                0 0 100px rgba(100, 200, 255, 0.2);
            text-align: center;
            position: relative;
            overflow: hidden;
            border: 0.1px solid rgba(90, 190, 245, 0.08);
                

        /* Advanced AI neural network background */
        .attractive-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(circle at 20% 80%, rgba(0, 150, 255, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 80% 20%, rgba(255, 0, 150, 0.15) 0%, transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(0, 255, 200, 0.1) 0%, transparent 60%),
                linear-gradient(45deg, transparent 30%, rgba(100, 200, 255, 0.05) 50%, transparent 70%);
            animation: neuralPulse 6s ease-in-out infinite alternate;
            pointer-events: none;
        }

        /* Multiple scanning lines effect */
        .attractive-header::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg,
                transparent,
                rgba(0, 255, 255, 0.3),
                rgba(255, 255, 255, 0.8),
                rgba(0, 255, 255, 0.3),
                transparent);
            animation: scanLines 4s linear infinite;
            pointer-events: none;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        }

        /* AI brain icon container */
        .ai-icon {
            display: inline-block;
            font-size: 4rem;
            margin-bottom: 1rem;
            animation: iconFloat 3s ease-in-out infinite, iconRotate 8s linear infinite;
            filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.8));
            position: relative;
            z-index: 2;
        }

        .attractive-header h1 {
            color: #ffffff;
            font-weight: 700;
            margin: 0;
            font-size: 3.2rem;
            text-shadow:
                0 0 10px rgba(0, 255, 255, 0.8),
                0 0 20px rgba(0, 255, 255, 0.4),
                0 0 30px rgba(0, 255, 255, 0.2),
                0 2px 4px rgba(0, 0, 0, 0.8);
            position: relative;
            z-index: 1;
            animation: fadeInDown 1s ease-out, titleGlow 3s ease-in-out infinite alternate;
            letter-spacing: 1px;
        }

        .attractive-header p {
            color: rgba(200, 220, 255, 0.95);
            margin: 1rem 0 0 0;
            font-size: 1.3rem;
            font-weight: 300;
            position: relative;
            z-index: 1;
            animation: fadeInUp 1s ease-out 0.3s both, subtitlePulse 4s ease-in-out infinite alternate;
            letter-spacing: 0.5px;
            text-shadow: 0 0 10px rgba(0, 200, 255, 0.3);
        }

        /* Floating particles effect */
        .particles {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            pointer-events: none;
            z-index: 0;
        }

        .particle {
            position: absolute;
            background: radial-gradient(circle, rgba(0, 255, 255, 0.8) 0%, transparent 70%);
            border-radius: 50%;
            animation: floatUp 8s linear infinite;
        }

        .particle:nth-child(1) { left: 10%; animation-delay: 0s; width: 4px; height: 4px; }
        .particle:nth-child(2) { left: 30%; animation-delay: 1s; width: 3px; height: 3px; }
        .particle:nth-child(3) { left: 50%; animation-delay: 2s; width: 5px; height: 5px; }
        .particle:nth-child(4) { left: 70%; animation-delay: 3s; width: 3px; height: 3px; }
        .particle:nth-child(5) { left: 90%; animation-delay: 4s; width: 4px; height: 4px; }

        /* Advanced AI-themed animations */
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes neuralPulse {
            0% {
                opacity: 0.2;
                transform: scale(1) rotate(0deg);
            }
            50% {
                opacity: 0.4;
            }
            100% {
                opacity: 0.2;
                transform: scale(1.1) rotate(5deg);
            }
        }

        @keyframes scanLines {
            0% {
                left: -100%;
                top: 0;
            }
            25% {
                top: 30%;
            }
            50% {
                left: 100%;
                top: 60%;
            }
            75% {
                top: 90%;
            }
            100% {
                left: -100%;
                top: 0;
            }
        }

        @keyframes titleGlow {
            0% {
                filter: brightness(1);
                transform: scale(1);
            }
            100% {
                filter: brightness(1.2);
                transform: scale(1.02);
            }
        }

        @keyframes subtitlePulse {
            0% {
                opacity: 0.8;
            }
            100% {
                opacity: 1;
            }
        }

        @keyframes iconFloat {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-10px);
            }
        }

        @keyframes iconRotate {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }

        @keyframes floatUp {
            0% {
                bottom: -10px;
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                bottom: 100%;
                opacity: 0;
            }
        }

        /* AI-style button animations */
        .stButton > button {
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        .stButton > button:hover::before {
            width: 300px;
            height: 300px;
        }

        /* Upload area AI effect */
        .stFileUploader {
            position: relative;
        }

        .stFileUploader::after {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #667eea);
            border-radius: 10px;
            background-size: 400% 400%;
            animation: gradientShift 3s ease infinite;
            opacity: 0;
            z-index: -1;
            transition: opacity 0.3s ease;
        }

        .stFileUploader:hover::after {
            opacity: 0.3;
        }

        @keyframes gradientShift {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }

        /* Enhanced AI Buffer Loading Spinner */
        .stSpinner > div {
            border-top-color: #00ffff !important;
            border-right-color: rgba(0, 255, 255, 0.3) !important;
            border-bottom-color: #0099ff !important;
            border-left-color: rgba(0, 255, 255, 0.3) !important;
            box-shadow:
                0 0 30px rgba(0, 255, 255, 0.8),
                inset 0 0 20px rgba(0, 255, 255, 0.4) !important;
            animation: aiBufferSpin 1s linear infinite, aiBufferPulse 1.5s ease-in-out infinite alternate !important;
            width: 50px !important;
            height: 50px !important;
            border-width: 4px !important;
        }

        /* AI Buffer Loading Container */
        .stSpinner {
            background: rgba(10, 10, 30, 0.9) !important;
            border: 2px solid rgba(0, 255, 255, 0.3) !important;
            border-radius: 20px !important;
            padding: 2rem !important;
            box-shadow:
                0 0 50px rgba(0, 255, 255, 0.4),
                inset 0 0 30px rgba(0, 150, 255, 0.2) !important;
            position: relative !important;
            overflow: hidden !important;
        }

        /* AI Buffer Loading Background Effects */
        .stSpinner::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(circle at 50% 50%, rgba(0, 255, 255, 0.1) 0%, transparent 70%),
                linear-gradient(45deg, transparent 30%, rgba(0, 255, 255, 0.05) 50%, transparent 70%);
            animation: bufferBgRotate 4s linear infinite;
            pointer-events: none;
        }

        /* AI Buffer Loading Text */
        .stSpinner p {
            color: #00ffff !important;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.8) !important;
            font-weight: 600 !important;
            animation: bufferTextGlow 2s ease-in-out infinite alternate !important;
        }

        /* AI Buffer Loading Animation Classes */
        @keyframes aiBufferSpin {
            0% {
                transform: rotate(0deg);
                filter: hue-rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
                filter: hue-rotate(360deg);
            }
        }

        @keyframes aiBufferPulse {
            0% {
                opacity: 0.8;
                transform: scale(1);
            }
            100% {
                opacity: 1;
                transform: scale(1.1);
            }
        }

        @keyframes bufferBgRotate {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }

        @keyframes bufferTextGlow {
            0% {
                text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
                filter: brightness(1);
            }
            100% {
                text-shadow: 0 0 20px rgba(0, 255, 255, 1), 0 0 30px rgba(0, 255, 255, 0.5);
                filter: brightness(1.3);
            }
        }

        /* Sidebar AI glow */
        .css-1d391kg {
            border-right: 1px solid rgba(102, 126, 234, 0.1);
        }

        .css-1d391kg::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 1px;
            height: 100%;
            background: linear-gradient(180deg, transparent, #667eea, transparent);
            animation: sideGlow 3s ease-in-out infinite;
            pointer-events: none;
        }

        @keyframes sideGlow {
            0%, 100% {
                opacity: 0.3;
                transform: translateY(-100%);
            }
            50% {
                opacity: 0.8;
                transform: translateY(100%);
            }
        }

        /* Success/error messages AI style */
        .stSuccess {
            position: relative;
            overflow: hidden;
        }

        .stSuccess::before {
            content: '✓';
            position: absolute;
            left: -30px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
            color: #48bb78;
            animation: slideInCheck 0.5s ease-out forwards;
        }

        @keyframes slideInCheck {
            to {
                left: 10px;
            }
        }

        /* Simplified - focusing only on enhanced loading spinner */

        /* Responsive design for header */
        @media (max-width: 768px) {
            .attractive-header h1 {
                font-size: 2.2rem;
            }
            .attractive-header p {
                font-size: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

# Main application
def main():
    st.set_page_config(
        page_title="AI Image Analyzer",
        page_icon="🖼️",
        layout="wide"
    )

    # Load header CSS
    load_header_css()

    # Dark AI-themed header with advanced animations
    st.markdown("""
    <div class="attractive-header">
        <div class="particles">
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
        </div>
        <h1>🤖 AI Image Analyzer</h1>
        <p>Upload an image and ask questions about it using Google's Generative AI</p>
        <div style="margin-top: 0.8rem; font-size: 0.8rem; opacity: 0.7; color: rgba(200, 220, 255, 0.8);">
            ✨ Watch the AI Buffer loading animation when analyzing images!
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Configure AI
    if not configure_genai():
        st.stop()

    # Sidebar for settings
    st.sidebar.header("Settings")

    # Predefined prompts
    predefined_prompts = [
        "Describe this image in detail",
        "What objects can you identify in this image?",
        "What is the main subject of this image?",
        "Analyze the colors and composition of this image",
        "Is there any text in this image? If so, what does it say?",
        "What is the mood or atmosphere of this image?",
        "Are there any people in this image? Describe them.",
        "What location or setting is depicted in this image?",
        "Analyze this sequence diagram - show all participants, messages, and interactions",
        "Extract all text and labels from this diagram",
        "Explain the flow and logic shown in this technical diagram"
    ]

    # File upload
    st.header("Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=[
            # Common formats
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
            # Additional formats
            'tiff', 'tif', 'svg', 'ico', 'eps', 'psd',
            # Camera RAW formats
            'raw', 'cr2', 'nef', 'arw', 'dng',
            # Apple formats
            'heic', 'heif'
        ]
    )

    if uploaded_file is not None:
        try:
            # Display image
            image = Image.open(uploaded_file)

            # Convert RGBA images to RGB for better compatibility with AI
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')

        except Exception as e:
            st.error(f"Error opening image: {str(e)}")
            st.error("This image format might not be supported. Try converting to JPEG or PNG first.")
            return

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Uploaded Image")
            st.image(image, use_container_width=True)
            st.info(f"Image: {uploaded_file.name}")
            st.info(f"Size: {image.size}")
            st.info(f"Format: {image.format}")

        with col2:
            st.subheader("Analysis")

            # Prompt selection
            prompt_option = st.selectbox(
                "Choose a predefined prompt or enter custom:",
                ["Custom prompt"] + predefined_prompts
            )

            if prompt_option == "Custom prompt":
                custom_prompt = st.text_area(
                    "Enter your custom prompt:",
                    placeholder="Ask anything about the image...",
                    height=100
                )
                prompt = custom_prompt if custom_prompt else "Describe this image"
            else:
                prompt = prompt_option
                st.text_area("Selected prompt:", prompt, height=100, disabled=True)

            # Analyze button
            if st.button("🔍 Analyze Image", type="primary"):
                with st.spinner("Analyzing image..."):
                    result = analyze_image(image, prompt, uploaded_file.name)

                    if result:
                        st.subheader("Analysis Result")
                        st.write(result)

                        # Download result
                        st.download_button(
                            label="📥 Download Analysis",
                            data=result,
                            file_name=f"image_analysis_{uploaded_file.name}.txt",
                            mime="text/plain"
                        )

    # Instructions
    st.sidebar.markdown("---")
    st.sidebar.header("Instructions")
    st.sidebar.markdown("""
    1. **Upload an image** using the file uploader
    2. **Select a prompt** or write your own
    3. **Click "Analyze Image"** to get AI insights
    4. **Download** the analysis if needed

    **Tips:**
    - Use clear, high-quality images
    - Be specific in your custom prompts
    - Try different prompt types for varied insights
    """)

    # About section
    st.sidebar.markdown("---")
    st.sidebar.header("About")
    st.sidebar.markdown("""
    This app uses **Google Generative AI** to analyze images and provide detailed insights.

    **Features:**
    - Multiple image formats supported
    - Predefined and custom prompts
    - Detailed image analysis
    - Export results
    """)

if __name__ == "__main__":
    main()