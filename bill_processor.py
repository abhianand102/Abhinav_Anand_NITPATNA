import re
from rule_based_parser import RuleBasedBillParser
from llm_enhancer import LLMEnhancer

class BillProcessor:
    def __init__(self):
        self.rule_parser = RuleBasedBillParser()
        self.llm_enhancer = LLMEnhancer()
        
    def extract_bill_data(self, pages_data):
        """Extract bill data with enhancement"""
        try:
            # Step 1: Rule-based parsing
            extracted_data = self.rule_parser.parse_bill_text(pages_data)
            
            # Step 2: Enhancement
            combined_text = " ".join([page['text'] for page in pages_data])
            extracted_data = self.llm_enhancer.enhance_extraction(combined_text, extracted_data)
            
            # Step 3: Final validation
            extracted_data = self._clean_and_validate_data(extracted_data)
            
            # Calculate token usage
            token_usage = {
                "total_tokens": self.llm_enhancer.get_token_count(),
                "input_tokens": self.llm_enhancer.get_input_tokens(),
                "output_tokens": self.llm_enhancer.get_output_tokens()
            }
            
            return extracted_data, token_usage
            
        except Exception as e:
            raise Exception(f"Bill processing failed: {str(e)}")
    
    def _clean_and_validate_data(self, data):
        """Clean and validate extracted data"""
        total_items = 0
        for page in data.get('pagewise_line_items', []):
            total_items += len(page.get('bill_items', []))
        
        data['total_item_count'] = total_items
        return data