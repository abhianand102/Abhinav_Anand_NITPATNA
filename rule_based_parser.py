import re  # Using Python's built-in re module
import json
from typing import List, Dict, Any

class RuleBasedBillParser:
    def __init__(self):
        self.total_patterns = [
            r'[Tt]otal\s+[\$]?\s*(\d+[.,]?\d*\.?\d{0,2})',
            r'[Ff]inal\s+[Tt]otal\s+[\$]?\s*(\d+[.,]?\d*\.?\d{0,2})',
            r'[Gg]rand\s+[Tt]otal\s+[\$]?\s*(\d+[.,]?\d*\.?\d{0,2})',
            r'[Bb]alance\s+[Dd]ue\s+[\$]?\s*(\d+[.,]?\d*\.?\d{0,2})',
        ]

    def detect_page_type(self, text: str) -> str:
        """Detect page type based on content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['pharmacy', 'medical', 'drug', 'medicine', 'hospital']):
            return 'Pharmacy'
        elif any(word in text_lower for word in ['final bill', 'summary', 'amount due']):
            return 'Final Bill'
        elif any(word in text_lower for word in ['detail', 'item', 'description', 'particulars']):
            return 'Bill Detail'
        else:
            return 'Bill Detail'

    def extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items using multiple pattern matching"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
                
            # Skip lines that are clearly headers or totals
            skip_keywords = ['total', 'subtotal', 'balance', 'due', 'amount', 'tax', 'discount']
            if any(keyword in line.lower() for keyword in skip_keywords):
                continue
                
            # Try different patterns
            item_data = self._parse_line_with_patterns(line)
            if item_data and self._is_valid_item(item_data):
                items.append(item_data)
        
        return items

    def _parse_line_with_patterns(self, line: str) -> Dict[str, Any]:
        """Try multiple patterns to parse a line"""
        
        # Pattern 1: Simple item with amount (Consultation $100.00)
        pattern1 = r'^([A-Za-z][A-Za-z\s\-\&\.\,]+?)\s+[\$]?\s*(\d+[.,]?\d*\.?\d{1,2})\s*$'
        match = re.search(pattern1, line)
        if match:
            name = self._clean_name(match.group(1))
            amount = self._parse_amount(match.group(2))
            if amount > 0:
                return {
                    'item_name': name,
                    'item_amount': amount,
                    'item_rate': amount,
                    'item_quantity': 1.0
                }
        
        # Pattern 2: Item with quantity and rate (Medicine 2 x $50.00 = $100.00)
        pattern2 = r'^([A-Za-z][A-Za-z\s\-\&\.\,]+?)\s+(\d+)\s*x\s*[\$]?\s*(\d+[.,]?\d*\.?\d{1,2})\s*=\s*[\$]?\s*(\d+[.,]?\d*\.?\d{1,2})'
        match = re.search(pattern2, line)
        if match:
            name = self._clean_name(match.group(1))
            quantity = float(match.group(2))
            rate = self._parse_amount(match.group(3))
            amount = self._parse_amount(match.group(4))
            if amount > 0:
                return {
                    'item_name': name,
                    'item_quantity': quantity,
                    'item_rate': rate,
                    'item_amount': amount
                }
        
        # Pattern 3: Tabular format with multiple numbers
        pattern3 = r'^([A-Za-z][A-Za-z\s\-\&\.\,]+?)\s+(\d+[.,]?\d*\.?\d{1,2})\s+(\d+[.,]?\d*\.?\d{1,2})\s+(\d+[.,]?\d*\.?\d{1,2})'
        match = re.search(pattern3, line)
        if match:
            name = self._clean_name(match.group(1))
            col1 = self._parse_amount(match.group(2))
            col2 = self._parse_amount(match.group(3))
            col3 = self._parse_amount(match.group(4))
            
            # Heuristic: largest number is usually the amount
            amounts = [col1, col2, col3]
            amount = max(amounts)
            if amount > 0:
                return {
                    'item_name': name,
                    'item_rate': col1,
                    'item_quantity': col2 if col2 > 0 and col2 < 1000 else 1.0,
                    'item_amount': col3
                }
        
        return None

    def _clean_name(self, name: str) -> str:
        """Clean item name"""
        name = re.sub(r'\s+', ' ', name.strip())
        # Remove trailing special characters and numbers
        name = re.sub(r'[\d\$\-\=\.\,]+$', '', name).strip()
        return name if name else "Unknown Item"

    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling commas"""
        try:
            # Remove currency symbols and spaces
            cleaned = re.sub(r'[^\d.,]', '', amount_str)
            
            # Handle different number formats
            if ',' in cleaned and '.' in cleaned:
                # If both comma and dot present, determine format
                if cleaned.rfind(',') > cleaned.rfind('.'):
                    # European format: 1.000,00 -> 1000.00
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    # US format: 1,000.00 -> 1000.00
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                # If only comma present, check if it's decimal or thousands
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) == 2:
                    # European decimal: 1000,00 -> 1000.00
                    cleaned = cleaned.replace(',', '.')
                else:
                    # US thousands: 1,000 -> 1000
                    cleaned = cleaned.replace(',', '')
            
            return float(cleaned) if cleaned else 0.0
        except (ValueError, AttributeError):
            return 0.0

    def _is_valid_item(self, item: Dict[str, Any]) -> bool:
        """Validate if extracted item is reasonable"""
        return (item['item_amount'] > 0 and 
                item['item_amount'] < 100000 and
                len(item['item_name']) > 2 and
                not any(word in item['item_name'].lower() for word in ['total', 'subtotal', 'tax']))

    def parse_bill_text(self, pages_data: List[Dict]) -> Dict[str, Any]:
        """Main method to parse bill text into structured format"""
        pagewise_items = []
        all_items = []
        
        for page in pages_data:
            page_text = page['text']
            page_no = page['page_no']
            
            page_type = self.detect_page_type(page_text)
            line_items = self.extract_line_items(page_text)
            
            # Filter out duplicates
            valid_items = []
            seen_items = set()
            
            for item in line_items:
                item_key = f"{item['item_name'].lower()}_{item['item_amount']:.2f}"
                if item_key not in seen_items:
                    valid_items.append(item)
                    seen_items.add(item_key)
            
            page_data = {
                'page_no': str(page_no),
                'page_type': page_type,
                'bill_items': valid_items
            }
            
            pagewise_items.append(page_data)
            all_items.extend(valid_items)
        
        return {
            'pagewise_line_items': pagewise_items,
            'total_item_count': len(all_items)
        }