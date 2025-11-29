import requests
import json
from free_llm_client import FreeLLMClient

class AccuracyTester:
    def __init__(self):
        self.llm_client = FreeLLMClient()
        self.base_url = "http://localhost:5000"
    
    def test_accuracy(self, test_cases):
        """Test accuracy with known test cases"""
        results = []
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            
            # Extract using our API
            api_result = self._extract_with_api(test_case['document_url'])
            
            if api_result and api_result['is_success']:
                # Calculate accuracy metrics
                accuracy = self._calculate_accuracy(api_result['data'], test_case['expected_data'])
                results.append({
                    'test_case': test_case['name'],
                    'accuracy': accuracy,
                    'api_result': api_result['data'],
                    'expected': test_case['expected_data']
                })
                
                print(f"📊 Accuracy: {accuracy['overall_accuracy']}%")
                print(f"✅ Items Match: {accuracy['items_accuracy']}%")
                print(f"💰 Total Match: {accuracy['total_accuracy']}%")
            else:
                print(f"❌ Extraction failed for {test_case['name']}")
        
        return results
    
    def _extract_with_api(self, document_url):
        """Extract data using our API"""
        try:
            response = requests.post(
                f"{self.base_url}/extract-bill-data",
                json={"document": document_url},
                timeout=120
            )
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    def _calculate_accuracy(self, extracted_data, expected_data):
        """Calculate accuracy metrics"""
        # Compare extracted items with expected items
        extracted_items = []
        for page in extracted_data.get('pagewise_line_items', []):
            extracted_items.extend(page.get('bill_items', []))
        
        expected_items = expected_data.get('items', [])
        
        # Simple item matching (by name and amount)
        matched_items = 0
        for exp_item in expected_items:
            for ext_item in extracted_items:
                if (self._normalize_name(exp_item['name']) in self._normalize_name(ext_item['item_name']) and
                    abs(exp_item['amount'] - ext_item['item_amount']) < 0.01):
                    matched_items += 1
                    break
        
        items_accuracy = (matched_items / len(expected_items)) * 100 if expected_items else 0
        
        # Total amount accuracy
        extracted_total = sum(item['item_amount'] for item in extracted_items)
        expected_total = expected_data.get('total_amount', 0)
        total_accuracy = 100 - (abs(extracted_total - expected_total) / expected_total * 100) if expected_total > 0 else 0
        
        overall_accuracy = (items_accuracy + total_accuracy) / 2
        
        return {
            'overall_accuracy': round(overall_accuracy, 2),
            'items_accuracy': round(items_accuracy, 2),
            'total_accuracy': round(total_accuracy, 2),
            'extracted_items_count': len(extracted_items),
            'expected_items_count': len(expected_items),
            'extracted_total': extracted_total,
            'expected_total': expected_total
        }
    
    def _normalize_name(self, name):
        """Normalize item name for comparison"""
        return ''.join(c for c in name.lower() if c.isalnum())

# Sample test cases (you'll need to create these with known bills)
sample_test_cases = [
    {
        "name": "Simple Medical Bill",
        "document_url": "https://example.com/sample-bill.jpg",  # Replace with actual URL
        "expected_data": {
            "items": [
                {"name": "Consultation", "amount": 500.0},
                {"name": "Medicine", "amount": 250.0}
            ],
            "total_amount": 750.0
        }
    }
]

if __name__ == "__main__":
    tester = AccuracyTester()
    
    print("🎯 ACCURACY TESTING FRAMEWORK")
    print("=" * 50)
    
    # For now, we'll test with the available samples
    results = tester.test_accuracy(sample_test_cases)
    
    if results:
        print(f"\n📈 OVERALL RESULTS:")
        avg_accuracy = sum(r['accuracy']['overall_accuracy'] for r in results) / len(results)
        print(f"Average Accuracy: {avg_accuracy:.2f}%")
    else:
        print("\n💡 To test accuracy, add real bill test cases with known expected results")