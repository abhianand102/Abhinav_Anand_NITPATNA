import requests
import pytesseract
from PIL import Image, ImageEnhance
import io
import pdf2image
import re
import urllib3
import base64

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_file(url):
    """Download file from URL or decode base64 data"""
    try:
        print(f"🔗 Processing: {url[:100]}...")
        
        # Check if it's a base64 data URL
        if url.startswith('data:image'):
            print("📸 Processing base64 image...")
            return decode_base64_image(url)
        
        # Regular URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=30, headers=headers, verify=False)
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.reason}")
        
        print(f"✅ Downloaded {len(response.content)} bytes")
        return response.content
        
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

def decode_base64_image(data_url):
    """Extract image from base64 data URL"""
    try:
        if 'base64,' in data_url:
            base64_data = data_url.split('base64,')[1]
        else:
            base64_data = data_url
            
        image_data = base64.b64decode(base64_data)
        print(f"✅ Decoded base64 image: {len(image_data)} bytes")
        return image_data
        
    except Exception as e:
        raise Exception(f"Base64 decoding failed: {str(e)}")

def preprocess_image(image):
    """Enhance image for better OCR results"""
    try:
        if image.mode != 'L':
            image = image.convert('L')
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        return image
    except Exception as e:
        print(f"Image preprocessing failed: {e}")
        return image

def extract_text_from_image(image_content):
    """Extract text from image using OCR"""
    try:
        image = Image.open(io.BytesIO(image_content))
        image = preprocess_image(image)
        
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        print(f"📝 OCR extracted: {len(text)} characters")
        return text
    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}")

def extract_text_from_pdf(pdf_content):
    """Extract text from PDF"""
    try:
        images = pdf2image.convert_from_bytes(pdf_content, dpi=200)
        pages_text = []
        
        for i, image in enumerate(images):
            processed_image = preprocess_image(image)
            text = pytesseract.image_to_string(processed_image)
            pages_text.append({
                'page_no': i + 1,
                'text': text
            })
        
        return pages_text
    except Exception as e:
        raise Exception(f"PDF processing failed: {str(e)}")

def detect_file_type(content):
    """Detect file type from content"""
    if content.startswith(b'%PDF'):
        return 'pdf'
    elif content.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    elif content.startswith(b'\x89PNG'):
        return 'png'
    else:
        return 'unknown'

def extract_text_from_document(document_content):
    """Extract text from document based on file type"""
    file_type = detect_file_type(document_content)
    print(f"🔍 Detected file type: {file_type}")
    
    if file_type == 'pdf':
        return extract_text_from_pdf(document_content)
    elif file_type in ['jpg', 'png', 'jpeg']:
        text = extract_text_from_image(document_content)
        return [{'page_no': 1, 'text': text}]
    else:
        raise Exception(f"Unsupported file format: {file_type}")