import requests
import json

def test_simple():
    base_url = "http://localhost:5000"
    
    print("📝 Testing with Simple Text")
    print("=" * 40)
    
    # Very simple bill text
    bill_text = "Consultation $200 Medicine $150 Lab Test $300 Total $650"
    
    try:
        response = requests.post(
            f"{base_url}/test-text",
            json={"text": bill_text},
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['is_success']}")
            
            if result['is_success']:
                data = result['data']
                print(f"📈 Items found: {data['total_item_count']}")
                
                for page in data['pagewise_line_items']:
                    for item in page['bill_items']:
                        print(f"   • {item['item_name']}: ${item['item_amount']}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_simple()