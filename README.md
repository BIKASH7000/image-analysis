# AI Image Analyzer

A powerful image analysis application built with Streamlit and Google Generative AI that allows you to upload images and get detailed AI-powered insights.

## Features

- 🖼️ **Multiple Image Formats**: Supports JPG, JPEG, PNG, GIF, BMP, and WebP
- 🤖 **AI-Powered Analysis**: Uses Google's Generative AI for intelligent image analysis
- 💬 **Flexible Prompts**: Choose from predefined prompts or create custom ones
- 📊 **Detailed Insights**: Get comprehensive descriptions and analysis of your images
- 💾 **Export Results**: Download analysis results as text files
- 🎨 **User-Friendly Interface**: Clean and intuitive Streamlit interface

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Generative AI API Key** - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Setup Instructions

### 1. Clone or Download the Project

```bash
git clone <repository-url> image-analyzer
cd image-analyzer
```

### 2. Create Virtual Environment

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file and add your Google API Key:
   ```
   GOOGLE_API_KEY=your_actual_google_api_key_here
   ```

## Usage

### Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### How to Use

1. **Upload an Image**: Click "Choose an image" and select an image file from your device
2. **Select or Enter a Prompt**:
   - Choose from predefined prompts like "Describe this image in detail"
   - Or write a custom prompt asking specific questions about the image
3. **Analyze**: Click the "Analyze Image" button
4. **View Results**: The AI analysis will appear on the right side
5. **Download**: Optionally download the analysis as a text file

## Supported Image Formats

### Common Formats
- **JPEG** (.jpg, .jpeg) - Most popular photo format
- **PNG** (.png) - With transparency support
- **GIF** (.gif) - Animated and static images
- **Bitmap** (.bmp) - Windows bitmap format
- **WebP** (.webp) - Modern web-optimized format

### Professional Formats
- **TIFF** (.tiff, .tif) - High-quality, lossless format
- **SVG** (.svg) - Scalable vector graphics
- **ICO** (.ico) - Windows icon format
- **EPS** (.eps) - Encapsulated PostScript
- **PSD** (.psd) - Photoshop document format

### Camera RAW Formats
- **RAW** (.raw) - Generic raw format
- **CR2** (.cr2) - Canon RAW format
- **NEF** (.nef) - Nikon RAW format
- **ARW** (.arw) - Sony RAW format
- **DNG** (.dng) - Adobe Digital Negative

### Apple Formats
- **HEIC** (.heic) - High Efficiency Image Container
- **HEIF** (.heif) - High Efficiency Image Format

**Total: 16+ image formats supported!**

## Example Prompts

### Predefined Prompts:
- "Describe this image in detail"
- "What objects can you identify in this image?"
- "What is the main subject of this image?"
- "Analyze the colors and composition of this image"
- "Is there any text in this image? If so, what does it say?"

### Custom Prompt Ideas:
- "What's the emotional tone of this image?"
- "Describe the lighting conditions in this photo"
- "What story does this image tell?"
- "Are there any safety hazards visible in this image?"
- "What kind of equipment or tools are shown?"

## Troubleshooting

### Common Issues:

1. **API Key Error**:
   - Ensure your Google API key is correctly set in the `.env` file
   - Make sure the API key has access to the Generative AI API

2. **Module Not Found**:
   - Make sure you've activated the virtual environment
   - Run `pip install -r requirements.txt` again

3. **Large Image Upload Issues**:
   - Try resizing large images before uploading
   - The app works best with images under 10MB

4. **Slow Analysis**:
   - Analysis time depends on image complexity and server load
   - Be patient for detailed analyses

## API Limits

- Google Generative AI has usage limits based on your API plan
- Be mindful of your API quota when analyzing many images
- Some analysis requests may take time to process

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Verify your Google API key and internet connection
3. Create an issue in the repository with details about the problem

---

**Built with ❤️ using Streamlit and Google Generative AI**