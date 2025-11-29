import os

class Config:
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    
    # File Processing Configuration
    MAX_FILE_SIZE = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'tiff'}
    
    # Tesseract Configuration
    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'