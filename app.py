from flask import Flask, request, jsonify
import requests
import json
import traceback
from utils import download_file, extract_text_from_document
from bill_processor import BillProcessor
from config import Config

app = Flask(__name__)
bill_processor = BillProcessor()

@app.route('/extract-bill-data', methods=['POST'])
def extract_bill_data():
    """
    Main API endpoint for bill data extraction - Python 3.13 Version
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'document' not in data:
            return jsonify({
                "is_success": False,
                "error": "Missing 'document' URL in request body",
                "token_usage": {
                    "total_tokens": 0,
                    "input_tokens": 0,
                    "output_tokens": 0
                }
            }), 400
        
        document_url = data['document']
        
        # Download document
        print(f"Downloading document from: {document_url}")
        document_content = download_file(document_url)
        
        # Extract text from document
        print("Extracting text from document...")
        pages_data = extract_text_from_document(document_content)
        
        # Check if we got any text
        all_text = " ".join([page['text'] for page in pages_data])
        if not all_text.strip():
            return jsonify({
                "is_success": False,
                "error": "No text could be extracted from the document",
                "token_usage": {
                    "total_tokens": 0,
                    "input_tokens": 0,
                    "output_tokens": 0
                }
            }), 400
        
        # Process bill data
        print("Processing bill data...")
        extracted_data, token_usage = bill_processor.extract_bill_data(pages_data)
        
        # Prepare success response
        response = {
            "is_success": True,
            "token_usage": token_usage,
            "data": extracted_data
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error processing request: {str(e)}")
        print(f"Traceback: {error_trace}")
        
        return jsonify({
            "is_success": False,
            "error": str(e),
            "token_usage": {
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0
            }
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Bill Extraction API (Python 3.13) is running"}), 200

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint with sample data"""
    sample_response = {
        "is_success": True,
        "token_usage": {
            "total_tokens": 150,
            "input_tokens": 100,
            "output_tokens": 50
        },
        "data": {
            "pagewise_line_items": [
                {
                    "page_no": "1",
                    "page_type": "Bill Detail",
                    "bill_items": [
                        {
                            "item_name": "Consultation Fee",
                            "item_amount": 500.0,
                            "item_rate": 500.0,
                            "item_quantity": 1.0
                        }
                    ]
                }
            ],
            "total_item_count": 1
        }
    }
    return jsonify(sample_response), 200

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )