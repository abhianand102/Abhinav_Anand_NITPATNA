import re  # Using built-in re

class FreeLLMClient:
    def __init__(self):
        # No external dependencies needed
        pass
        
    def enhance_extraction(self, text: str, rule_based_data: dict) -> dict:
        """
        Enhance rule-based extraction with pattern matching
        Using built-in re module
        """
        try:
            enhanced_data = self._validate_and_enhance_data(rule_based_data, text)
            return enhanced_data
        except Exception as e:
            print(f"Enhancement failed: {e}")
            return rule_based_data
    
    def _validate_and_enhance_data(self, data: dict, original_text: str) -> dict:
        """Validate and enhance extracted data with simple rules"""
        
        # Calculate total from extracted items
        total_calculated = 0
        for page in data.get('pagewise_line_items', []):
            for item in page.get('bill_items', []):
                total_calculated += item.get('item_amount', 0)
        
        # Try to find total in original text using built-in re
        extracted_total = self._extract_total_with_context(original_text)
        
        # Add validation information
        if extracted_total and abs(total_calculated - extracted_total) / extracted_total < 0.15:
            data['validation'] = {
                'total_match': True, 
                'difference': abs(total_calculated - extracted_total),
                'extracted_total': extracted_total,
                'calculated_total': total_calculated
            }
        else:
            data['validation'] = {
                'total_match': False, 
                'calculated_total': total_calculated,
                'extracted_total': extracted_total
            }
        
        return data
    
    def _extract_total_with_context(self, text: str) -> float:
        """Extract total amount with context awareness using built-in re"""
        total_patterns = [
            r'[Tt]otal\s+[Aa]mount\s*[\$]?\s*(\d+[.,]?\d*\.?\d{0,2})',
            r'[Gg]rand\s+[Tt]otal\s*[\$]?\s*(\d+[.,]?\d*\.?\d{0,2})',
            r'[Ff]inal\s+[Tt]otal\s*[\$]?\s*(\d+[.,]?\d*\.?\d{0,2})',
            r'[Bb]alance\s+[Dd]ue\s*[\$]?\s*(\d+[.,]?\d*\.?\d{0,2})',
            r'[Tt]otal\s*[\$]?\s*(\d+[.,]?\d*\.?\d{0,2})',
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    amount_str = match.group(1)
                    # Clean and parse amount
                    cleaned = re.sub(r'[^\d.,]', '', amount_str)
                    if ',' in cleaned and '.' in cleaned:
                        if cleaned.rfind(',') > cleaned.rfind('.'):
                            cleaned = cleaned.replace('.', '').replace(',', '.')
                        else:
                            cleaned = cleaned.replace(',', '')
                    elif ',' in cleaned:
                        parts = cleaned.split(',')
                        if len(parts) == 2 and len(parts[1]) == 2:
                            cleaned = cleaned.replace(',', '.')
                        else:
                            cleaned = cleaned.replace(',', '')
                    
                    amount = float(cleaned) if cleaned else 0.0
                    if amount > 0 and amount < 1000000:
                        return amount
                except ValueError:
                    continue
        
        return None