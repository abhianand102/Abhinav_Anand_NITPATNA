from flask import Flask, request, jsonify
from utils import download_file, extract_text_from_document
from bill_processor import BillProcessor
from config import Config

app = Flask(__name__)
bill_processor = BillProcessor()

@app.route('/extract-bill-data', methods=['POST'])
def extract_bill_data():
    """Main API endpoint for bill data extraction"""
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
        
        # Download and process document
        document_content = download_file(document_url)
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
        
        # Process bill data with LLM enhancement
        extracted_data, token_usage = bill_processor.extract_bill_data(pages_data)
        
        # Prepare success response
        response = {
            "is_success": True,
            "token_usage": token_usage,
            "data": extracted_data
        }
        
        return jsonify(response), 200
        
    except Exception as e:
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
    return jsonify({
        "status": "healthy", 
        "message": "Bill Extraction API with Free LLM Enhancement",
        "version": "2.0"
    }), 200

@app.route('/')
def home():
    return jsonify({
        "message": "Bill Extraction API with Free LLM",
        "endpoint": "POST /extract-bill-data",
        "example_request": {
            "document": "https://example.com/your-bill.jpg"
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)