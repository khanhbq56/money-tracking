import google.generativeai as genai
from django.conf import settings
import re
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, date
from .date_parser import DateParser

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self, language='vi'):
        """Initialize Gemini service with language support"""
        self.language = language
        self.model = None
        self.date_parser = DateParser(language)
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini API with proper error handling"""
        try:
            if not settings.GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY not configured, falling back to simple categorization")
                return
            
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self.model = None
    
    def categorize_transaction(self, message: str, has_voice: bool = False) -> Dict[str, Any]:
        """Analyze user message and categorize transaction with date parsing"""
        try:
            # Parse date from message using DateParser
            parsed_date = self.date_parser.parse_date_from_message(message)
            
            if self.model:
                # Use Gemini AI for categorization
                result = self._categorize_with_gemini(message)
            else:
                # Fallback to simple categorization
                result = self._fallback_categorization(message)
            
            # Add metadata
            result['parsed_date'] = parsed_date.isoformat()
            result['parsed_date_description'] = self.date_parser.get_relative_description(parsed_date)
            result['has_voice'] = has_voice
            result['language'] = self.language
            
            return result
            
        except Exception as e:
            logger.error(f"Error in categorize_transaction: {e}")
            parsed_date = self.date_parser.parse_date_from_message(message)
            return self._fallback_categorization(message, has_voice, parsed_date)
    
    def _categorize_with_gemini(self, message: str) -> Dict[str, Any]:
        """Use Gemini AI for transaction categorization"""
        prompt = self._build_prompt(message, self.language)
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            response_text = response.text.strip()
            # Clean up response in case it contains markdown formatting
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text)
            
            # Validate and normalize the response
            return self._validate_ai_result(result, message)
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Fall back to simple categorization
            return self._fallback_categorization(message)
    
    def _build_prompt(self, message: str, language: str) -> str:
        """Build appropriate prompt based on language"""
        from django.utils.translation import gettext as _
        
        # Use translation system for prompt template
        prompt_template = _('gemini_prompt_template')
        
        return prompt_template.format(message=message)
    
    def _validate_ai_result(self, result: Dict[str, Any], original_message: str) -> Dict[str, Any]:
        """Validate and normalize AI result"""
        # Ensure required fields exist
        validated = {
            'type': result.get('type', 'expense'),
            'amount': abs(float(result.get('amount', 0))),
            'description': result.get('description', original_message[:50]),
            'category': result.get('category'),
            'confidence': max(0.6, min(1.0, float(result.get('confidence', 0.8)))),
            'icon': result.get('icon', '📦')
        }
        
        # Validate type
        if validated['type'] not in ['expense', 'saving', 'investment']:
            validated['type'] = 'expense'
        
        # Validate category for expenses only
        if validated['type'] == 'expense':
            valid_categories = ['food', 'coffee', 'transport', 'shopping', 'entertainment', 'health', 'education', 'utilities', 'other']
            if validated['category'] not in valid_categories:
                validated['category'] = 'other'
        else:
            validated['category'] = None
        
        # Ensure minimum amount
        if validated['amount'] < 1000:
            validated['amount'] = validated['amount'] * 1000  # Assume thousands
        
        return validated
    
    def _fallback_categorization(self, message: str, has_voice: bool = False, parsed_date: Optional[date] = None) -> Dict[str, Any]:
        """Simple regex-based categorization fallback"""
        message_lower = message.lower()
        amount = self._extract_amount_fallback(message)
        
        # Default values
        result = {
            'type': 'expense',
            'amount': amount,
            'description': message[:50],
            'category': 'other',
            'confidence': 0.6,
            'icon': '📦',
            'has_voice': has_voice,
            'parsed_date': (parsed_date or date.today()).isoformat(),
            'language': self.language
        }
        
        # Coffee detection
        if any(word in message_lower for word in ['coffee', 'cafe', 'cà phê']):
            result.update({
                'type': 'expense',
                'category': 'coffee',
                'icon': '☕',
                'description': 'Coffee',
                'confidence': 0.9
            })
        
        # Food detection
        elif any(word in message_lower for word in ['ăn', 'trưa', 'sáng', 'tối', 'phở', 'cơm', 'bún', 'lunch', 'dinner', 'food']):
            from .translation_utils import get_category_display_name
            result.update({
                'type': 'expense',
                'category': 'food',
                'icon': '🍜',
                'description': get_category_display_name('food', self.language),
                'confidence': 0.8
            })
        
        # Transport detection
        elif any(word in message_lower for word in ['grab', 'taxi', 'xe ôm', 'xăng', 'transport', 'fuel']):
            from .translation_utils import get_category_display_name
            result.update({
                'type': 'expense',
                'category': 'transport',
                'icon': '🚗',
                'description': get_category_display_name('transport', self.language),
                'confidence': 0.8
            })
        
        # Saving detection
        elif any(word in message_lower for word in ['tiết kiệm', 'gửi', 'save', 'saving']):
            from .translation_utils import get_category_display_name
            result.update({
                'type': 'saving',
                'category': None,
                'icon': '💰',
                'description': get_category_display_name('saving', self.language),
                'confidence': 0.9
            })
        
        # Investment detection
        elif any(word in message_lower for word in ['đầu tư', 'cổ phiếu', 'invest', 'stock', 'bitcoin']):
            from .translation_utils import get_category_display_name
            result.update({
                'type': 'investment',
                'category': None,
                'icon': '📈',
                'description': get_category_display_name('investment', self.language),
                'confidence': 0.8
            })
        
        return result
    
    def _extract_amount_fallback(self, message: str) -> float:
        """Extract amount from message using regex"""
        # Look for patterns like "25k", "1.5M", "100000"
        patterns = [
            r'(\d+(?:\.\d+)?)[kK]',  # 25k, 1.5k
            r'(\d+(?:\.\d+)?)[mM]',  # 1M, 1.5M
            r'(\d+(?:,\d{3})*)',     # 100,000
            r'(\d+)'                 # Simple number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                value = float(match.group(1).replace(',', ''))
                
                if 'k' in match.group(0).lower():
                    return value * 1000
                elif 'm' in match.group(0).lower():
                    return value * 1000000
                elif value < 1000:  # Assume thousands for small numbers
                    return value * 1000
                else:
                    return value
        
        return 50000  # Default amount if nothing found 