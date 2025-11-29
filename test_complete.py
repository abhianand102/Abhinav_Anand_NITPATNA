import requests
import json
import time

def test_complete_flow():
    base_url = "http://localhost:5000"
    
    print("🎯 COMPLETE BILL EXTRACTION TEST")
    print("=" * 60)
    
    # Test cases with WORKING URLs
    test_cases = [
        {
            "name": "Sample Receipt Image",
            "url": "https://templates.invoicehome.com/invoice-template-us-classic-white-750px.png",
            "type": "receipt"
        },
        {
            "name": "Sample Invoice", 
            "url": "https://www.zervant.com/images/example-invoice-zervant-en.png",
            "type": "invoice"
        },
        {
            "name": "Simple Text Image",
            "url": "https://i.ibb.co/0j7J2ZR/sample-text.png",  # We'll create this
            "type": "text"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"📁 URL: {test_case['url']}")
        
        try:
            # First, test if the URL is accessible
            print("   🔍 Checking URL accessibility...")
            head_response = requests.head(test_case['url'], timeout=10)
            if head_response.status_code != 200:
                print(f"   ⚠️  URL might not be accessible directly. Trying anyway...")
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/extract-bill-data",
                json={"document": test_case['url']},
                timeout=120
            )
            end_time = time.time()
            
            print(f"   ⏱️  Response Time: {end_time - start_time:.2f}s")
            print(f"   📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   ✅ Success: {result['is_success']}")
                
                if result['is_success']:
                    data = result['data']
                    print(f"   📈 Items Found: {data['total_item_count']}")
                    print(f"   📄 Pages: {len(data['pagewise_line_items'])}")
                    
                    # Display detailed results
                    for page in data['pagewise_line_items']:
                        print(f"\n   📑 Page {page['page_no']} ({page['page_type']}):")
                        if page['bill_items']:
                            for i, item in enumerate(page['bill_items'][:10]):  # Show first 10 items
                                print(f"      {i+1}. {item['item_name']}: ${item['item_amount']} (Qty: {item['item_quantity']}, Rate: ${item['item_rate']})")
                        else:
                            print("      No items extracted")
                    
                    # Show validation info if available
                    if 'validation' in data:
                        print(f"\n   🔍 Validation: {data['validation']}")
                        
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   💬 Error Message: {error_data.get('error', 'No error message')}")
                except:
                    print(f"   💬 Response Text: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("   ⚠️  Request timed out")
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎊 TESTING COMPLETED!")

def create_simple_test_image():
    """Create a simple test image with bill-like content"""
    print("\n📝 Creating a simple test image...")
    # This is a placeholder - in real scenario, you'd create an actual image
    test_content = """
    INVOICE
    =======
    
    ITEM                QTY    RATE    AMOUNT
    Consultation        1      $500    $500.00
    Medicine            2      $250    $500.00
    Lab Test            1      $300    $300.00
    
    SUBTOTAL: $1300.00
    TAX: $130.00
    TOTAL: $1430.00
    """
    
    print("💡 For local testing, save this text as an image file")
    print("   You can use online tools like: https://www.online-image-editor.com/")
    return test_content

if __name__ == "__main__":
    test_complete_flow()
    
    # Show how to test with local files
    print("\n" + "=" * 60)
    print("💡 LOCAL FILE TESTING INSTRUCTIONS:")
    print("1. Take a screenshot of a bill or create an image with text")
    print("2. Upload it to a free image hosting service like:")
    print("   - https://imgbb.com/")
    print("   - https://postimages.org/")
    print("   - https://imgur.com/")
    print("3. Use the direct image URL in the test above")