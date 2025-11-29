import requests
import json

def test_local():
    base_url = "http://localhost:5000"
    
    print("🚀 Testing Bill Extraction API")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Test with a simple bill image URL
    print("\n2. Testing bill extraction...")
    
    # Use a simple test image with text
    test_url = "https://via.placeholder.com/600x400/FFFFFF/000000?text=Sample+Bill%0A%0AItem+1:+$100.00%0AItem+2:+$200.00%0A%0ATotal:+$300.00"
    
    try:
        response = requests.post(
            f"{base_url}/extract-bill-data",
            json={"document": test_url},
            timeout=60
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['is_success']}")
            
            if result['is_success']:
                data = result['data']
                print(f"📈 Items found: {data['total_item_count']}")
                
                for page in data['pagewise_line_items']:
                    print(f"📄 Page {page['page_no']} ({page['page_type']}):")
                    for item in page['bill_items']:
                        print(f"   • {item['item_name']}: ${item['item_amount']}")
            else:
                print(f"❌ Error: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_local()