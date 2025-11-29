import re

class RuleBasedBillParser:
    def __init__(self):
        self.total_patterns = [
            r'(?i)total[\s:]*[\$]?\s*(\d+[.,]?\d*\.?\d{2})',
            r'(?i)grand total[\s:]*[\$]?\s*(\d+[.,]?\d*\.?\d{2})',
            r'(?i)final total[\s:]*[\$]?\s*(\d+[.,]?\d*\.?\d{2})'
        ]

    def detect_page_type(self, text):
        text_lower = text.lower()
        if any(word in text_lower for word in ['pharmacy', 'medical', 'drug']):
            return 'Pharmacy'
        elif any(word in text_lower for word in ['final bill', 'summary']):
            return 'Final Bill'
        else:
            return 'Bill Detail'

    def extract_line_items(self, text):
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if len(line) < 3:
                continue
                
            # Skip totals and headers
            if any(word in line.lower() for word in ['total', 'subtotal', 'balance']):
                continue
                
            item_data = self._parse_line(line)
            if item_data:
                items.append(item_data)
        
        return items

    def _parse_line(self, line):
        # Pattern 1: Simple item with amount
        pattern1 = r'^([A-Za-z][A-Za-z\s\-\&]+?)\s+[\$]?\s*(\d+\.?\d{2})\s*$'
        match = re.search(pattern1, line)
        if match:
            return {
                'item_name': match.group(1).strip(),
                'item_amount': float(match.group(2)),
                'item_rate': float(match.group(2)),
                'item_quantity': 1.0
            }
        
        # Pattern 2: Item with quantity
        pattern2 = r'^([A-Za-z][A-Za-z\s\-\&]+?)\s+(\d+)\s*x\s*[\$]?\s*(\d+\.?\d{2})'
        match = re.search(pattern2, line)
        if match:
            return {
                'item_name': match.group(1).strip(),
                'item_quantity': float(match.group(2)),
                'item_rate': float(match.group(3)),
                'item_amount': float(match.group(2)) * float(match.group(3))
            }
        
        return None

    def parse_bill_text(self, pages_data):
        pagewise_items = []
        all_items = []
        
        for page in pages_data:
            page_type = self.detect_page_type(page['text'])
            line_items = self.extract_line_items(page['text'])
            
            page_data = {
                'page_no': str(page['page_no']),
                'page_type': page_type,
                'bill_items': line_items
            }
            
            pagewise_items.append(page_data)
            all_items.extend(line_items)
        
        return {
            'pagewise_line_items': pagewise_items,
            'total_item_count': len(all_items)
        }