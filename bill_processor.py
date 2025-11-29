import re  # Using built-in re
from rule_based_parser import RuleBasedBillParser

class BillProcessor:
    def __init__(self):
        self.rule_parser = RuleBasedBillParser()
        
    def extract_bill_data(self, pages_data):
        """Main method to extract bill data using rule-based parsing"""
        try:
            print("Performing rule-based parsing...")
            extracted_data = self.rule_parser.parse_bill_text(pages_data)
            
            # Validate and clean data
            extracted_data = self._clean_and_validate_data(extracted_data)
            
            # Calculate token usage (mock for compatibility)
            token_usage = self._calculate_token_usage(extracted_data, pages_data)
            
            return extracted_data, token_usage
            
        except Exception as e:
            raise Exception(f"Bill processing failed: {str(e)}")
    
    def _clean_and_validate_data(self, data):
        """Clean and validate extracted data"""
        if 'pagewise_line_items' not in data:
            data['pagewise_line_items'] = []
        
        total_items = 0
        all_bill_items = []
        
        for page in data['pagewise_line_items']:
            if 'bill_items' not in page:
                page['bill_items'] = []
                
            # Clean item names and ensure required fields
            for item in page['bill_items']:
                item['item_name'] = self._clean_item_name(item.get('item_name', 'Unknown Item'))
                item['item_quantity'] = item.get('item_quantity', 1.0)
                item['item_rate'] = item.get('item_rate', item.get('item_amount', 0.0))
                item['item_amount'] = item.get('item_amount', 0.0)
            
            total_items += len(page['bill_items'])
            all_bill_items.extend(page['bill_items'])
        
        # Remove duplicates across all pages
        unique_items = self._remove_duplicate_items(all_bill_items)
        
        # Rebuild page structure with unique items
        cleaned_pages = []
        for page in data['pagewise_line_items']:
            page_items = page.get('bill_items', [])
            unique_page_items = []
            for item in page_items:
                if any(self._items_match(item, unique_item) for unique_item in unique_items):
                    unique_page_items.append(item)
            page['bill_items'] = unique_page_items
            cleaned_pages.append(page)
        
        data['pagewise_line_items'] = cleaned_pages
        data['total_item_count'] = len(unique_items)
        
        return data
    
    def _clean_item_name(self, name):
        """Clean item name using built-in re"""
        if not name or name == "Unknown Item":
            return "Unknown Item"
        
        # Remove extra spaces and clean up
        name = re.sub(r'\s+', ' ', name.strip())
        name = re.sub(r'^[^A-Za-z]*', '', name)
        name = re.sub(r'[^A-Za-z\s\-\&\.\,]+$', '', name)
        
        # Basic capitalization
        if name and any(c.isalpha() for c in name):
            words = name.split()
            capitalized_words = []
            for word in words:
                if word and word[0].isalpha():
                    capitalized_words.append(word[0].upper() + word[1:].lower())
                else:
                    capitalized_words.append(word)
            name = ' '.join(capitalized_words)
        
        return name if name and len(name) > 1 else "Unknown Item"
    
    def _remove_duplicate_items(self, items):
        """Remove duplicate items based on name and amount"""
        seen = set()
        unique_items = []
        
        for item in items:
            clean_name = re.sub(r'\s+', ' ', item['item_name'].lower().strip())
            key = (clean_name, round(item['item_amount'], 2))
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
        
        return unique_items
    
    def _items_match(self, item1, item2):
        """Check if two items are essentially the same"""
        name1 = re.sub(r'\s+', ' ', item1['item_name'].lower().strip())
        name2 = re.sub(r'\s+', ' ', item2['item_name'].lower().strip())
        return (name1 == name2 and 
                abs(item1['item_amount'] - item2['item_amount']) < 0.01)
    
    def _calculate_token_usage(self, extracted_data, pages_data):
        """Calculate mock token usage for compatibility"""
        input_text = " ".join([page['text'] for page in pages_data])
        output_text = str(extracted_data)
        
        input_tokens = len(input_text) // 4
        output_tokens = len(output_text) // 4
        
        return {
            "total_tokens": input_tokens + output_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }