import requests
import pytesseract
import pdf2image
import io
import re  # Using built-in re
import os

# Try to import PIL, but have fallback
try:
    from PIL import Image, ImageEnhance
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    print("Pillow not available, using basic image processing")

def download_file(url):
    """Download file from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise Exception(f"Failed to download file: {str(e)}")

def preprocess_image(image):
    """Enhance image for better OCR results"""
    if HAS_PILLOW:
        try:
            if image.mode != 'L':
                image = image.convert('L')
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            return image
        except Exception as e:
            print(f"Image preprocessing failed: {e}")
            return image
    else:
        return image

def extract_text_from_image(image_content):
    """Extract text from image using OCR"""
    try:
        if HAS_PILLOW:
            image = Image.open(io.BytesIO(image_content))
            image = preprocess_image(image)
        else:
            from pdf2image import Image as PdfImage
            image = PdfImage(io.BytesIO(image_content))
        
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        return text
    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}")

def extract_text_from_pdf(pdf_content):
    """Extract text from PDF with page-wise processing"""
    try:
        images = pdf2image.convert_from_bytes(pdf_content, dpi=200)
        pages_text = []
        
        for i, image in enumerate(images):
            if HAS_PILLOW:
                processed_image = preprocess_image(image)
            else:
                processed_image = image
                
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
    elif content.startswith(b'II*\x00') or content.startswith(b'MM\x00*'):
        return 'tiff'
    else:
        return 'unknown'

def extract_text_from_document(document_content):
    """Extract text from document based on file type"""
    file_type = detect_file_type(document_content)
    
    if file_type == 'pdf':
        return extract_text_from_pdf(document_content)
    elif file_type in ['jpg', 'png', 'jpeg', 'tiff']:
        text = extract_text_from_image(document_content)
        return [{'page_no': 1, 'text': text}]
    else:
        raise Exception(f"Unsupported file format: {file_type}")