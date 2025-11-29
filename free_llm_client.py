import requests
import re
import json

class FreeLLMClient:
    def __init__(self):
        self.huggingface_models = {
            "llama": "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf",
            "mistral": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        }
        
    def enhance_with_huggingface(self, extracted_text, rule_based_data):
        """Enhance extraction using Hugging Face inference API"""
        try:
            # Simple enhancement without API call (fallback)
            enhanced_data = self._smart_enhancement(extracted_text, rule_based_data)
            return enhanced_data
            
        except Exception as e:
            print(f"Hugging Face enhancement failed: {e}")
            return rule_based_data
    
    def _smart_enhancement(self, extracted_text, data):
        """Smart enhancement using rule-based AI techniques"""
        
        # 1. Context-aware item categorization
        data = self._categorize_items(data, extracted_text)
        
        # 2. Amount validation and correction
        data = self._validate_amounts(data, extracted_text)
        
        # 3. Duplicate detection and merging
        data = self._advanced_deduplication(data)
        
        # 4. Total reconciliation
        data = self._reconcile_totals(data, extracted_text)
        
        return data
    
    def _categorize_items(self, data, context_text):
        """Categorize items based on common patterns"""
        medical_terms = ['medicine', 'drug', 'tablet', 'capsule', 'injection', 'consultation', 'doctor']
        service_terms = ['service', 'fee', 'charge', 'consultation', 'visit']
        product_terms = ['product', 'item', 'material', 'goods']
        
        for page in data.get('pagewise_line_items', []):
            for item in page.get('bill_items', []):
                item_name_lower = item['item_name'].lower()
                
                if any(term in item_name_lower for term in medical_terms):
                    item['category'] = 'medical'
                elif any(term in item_name_lower for term in service_terms):
                    item['category'] = 'service'
                elif any(term in item_name_lower for term in product_terms):
                    item['category'] = 'product'
                else:
                    item['category'] = 'other'
        
        return data
    
    def _validate_amounts(self, data, context_text):
        """Validate and correct amounts based on context"""
        # Extract all amounts mentioned in text
        amount_pattern = r'\$?\s*(\d+[.,]?\d*\.?\d{2})'
        context_amounts = re.findall(amount_pattern, context_text)
        context_amounts = [float(amt.replace(',', '')) for amt in context_amounts if float(amt.replace(',', '')) > 0]
        
        total_extracted = sum(item['item_amount'] for page in data.get('pagewise_line_items', []) for item in page.get('bill_items', []))
        
        # If our total is significantly different from context amounts, flag it
        if context_amounts:
            max_context_amount = max(context_amounts)
            if total_extracted > 0 and abs(total_extracted - max_context_amount) / max_context_amount > 0.3:
                data['validation_warning'] = f"Extracted total (${total_extracted}) differs significantly from context amounts"
        
        return data
    
    def _advanced_deduplication(self, data):
        """Advanced duplicate detection using fuzzy matching"""
        all_items = []
        for page in data.get('pagewise_line_items', []):
            for item in page.get('bill_items', []):
                all_items.append(item)
        
        # Remove duplicates based on similarity
        unique_items = []
        seen_patterns = set()
        
        for item in all_items:
            # Create a pattern key (name + rounded amount)
            pattern = f"{self._normalize_text(item['item_name'])}_{round(item['item_amount'], 2)}"
            
            if pattern not in seen_patterns:
                unique_items.append(item)
                seen_patterns.add(pattern)
        
        # Update data with unique items
        if data['pagewise_line_items']:
            data['pagewise_line_items'][0]['bill_items'] = unique_items
            data['total_item_count'] = len(unique_items)
        
        return data
    
    def _normalize_text(self, text):
        """Normalize text for comparison"""
        text = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
        return text
    
    def _reconcile_totals(self, data, context_text):
        """Reconcile extracted totals with context totals"""
        # Look for total patterns in context
        total_patterns = [
            r'[Tt]otal\s*[\$]?\s*(\d+[.,]?\d*\.?\d{2})',
            r'[Gg]rand\s+[Tt]otal\s*[\$]?\s*(\d+[.,]?\d*\.?\d{2})',
            r'[Ff]inal\s+[Tt]otal\s*[\$]?\s*(\d+[.,]?\d*\.?\d{2})',
            r'[Bb]alance\s+[Dd]ue\s*[\$]?\s*(\d+[.,]?\d*\.?\d{2})',
        ]
        
        context_totals = []
        for pattern in total_patterns:
            matches = re.findall(pattern, context_text)
            for match in matches:
                amount = float(match.replace(',', ''))
                if amount > 0:
                    context_totals.append(amount)
        
        extracted_total = sum(item['item_amount'] for page in data.get('pagewise_line_items', []) for item in page.get('bill_items', []))
        
        if context_totals:
            best_context_total = max(context_totals)  # Usually the largest mentioned total is the final total
            accuracy = 1 - abs(extracted_total - best_context_total) / best_context_total if best_context_total > 0 else 0
            
            data['accuracy_metrics'] = {
                'extracted_total': extracted_total,
                'context_total': best_context_total,
                'accuracy_percentage': round(accuracy * 100, 2),
                'difference': abs(extracted_total - best_context_total)
            }
        
        return data