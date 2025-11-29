import requests
import json
import time

def test_health():
    """Test health endpoint"""
    url = "http://localhost:5000/health"
    try:
        response = requests.get(url)
        print(f"✅ Health Check Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_sample_bill():
    """Test with a sample bill URL"""
    url = "http://localhost:5000/extract-bill-data"
    
    # You can replace this with any bill image URL
    test_data = {
        "document": "https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/testing/eurotext.tif"
    }
    
    try:
        print("\n🧪 Testing bill extraction...")
        start_time = time.time()
        response = requests.post(url, json=test_data, timeout=120)
        end_time = time.time()
        
        print(f"✅ API Response Status: {response.status_code}")
        print(f"⏱️  Response Time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("📊 Extraction Results:")
            print(json.dumps(result, indent=2))
            
            if result.get('is_success'):
                total_items = result['data']['total_item_count']
                print(f"📈 Successfully extracted {total_items} items!")
            return True
        else:
            print(f"❌ API Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_local_file():
    """Test with a local file (if you have one)"""
    # This is for future use when you want to test with local files
    print("\n📁 Local file testing not implemented yet")
    print("💡 To test with local files, you'd need to:")
    print("   1. Host the file online (e.g., using GitHub, Imgur)")
    print("   2. Use the public URL in the test above")

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    print("=" * 50)
    
    # Test health endpoint first
    if test_health():
        # Then test bill extraction
        test_sample_bill()
    else:
        print("❌ Cannot proceed - API is not healthy")