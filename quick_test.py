import requests
import base64
from PIL import Image, ImageDraw
import io

def create_simple_bill_image():
    """Create a very simple bill image"""
    img = Image.new('RGB', (600, 300), color='white')
    d = ImageDraw.Draw(img)
    
    # Very simple text
    text = "Consultation $200\nMedicine $150\nTotal $350"
    
    d.text((50, 50), text, fill='black')
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/jpeg;base64,{img_str}"

def test_api():
    base_url = "http://localhost:5000"
    
    print("🚀 FINAL TEST")
    print("=" * 40)
    
    # Test 1: Health check
    print("1. Health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.status_code}")
    except Exception as e:
        print(f"❌ Health failed: {e}")
        return
    
    # Test 2: Test with base64 image
    print("\n2. Testing with base64 image...")
    
    base64_image = create_simple_bill_image()
    
    try:
        response = requests.post(
            f"{base_url}/extract-bill-data",
            json={"document": base64_image},
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
                    for item in page['bill_items']:
                        print(f"   • {item['item_name']}: ${item['item_amount']}")
            else:
                print(f"❌ Error: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_api()