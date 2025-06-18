"""
Bank Email AI Parser using Gemini
Extends existing GeminiService for bank transaction email parsing
"""
import logging
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from ai_chat.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class BankEmailAIParser(GeminiService):
    """
    AI parser for bank emails - extends existing GeminiService
    Reuses existing model initialization and language support
    """
    
    def __init__(self, language='vi'):
        """Initialize with existing GeminiService infrastructure"""
        super().__init__(language)
        self.bank_prompts = self._get_bank_prompts()
    
    def _get_bank_prompts(self) -> Dict[str, Dict[str, str]]:
        """Get bank-specific prompts in Vietnamese and English"""
        return {
            'tpbank': {
                'vi': """
Bạn là AI chuyên phân tích email giao dịch ngân hàng TPBank. 
Nhiệm vụ: Trích xuất thông tin giao dịch chính xác từ email và trả về JSON.

Quy tắc phân loại:
- transaction_type: "expense" (tiền ra), "saving" (tiền vào tiết kiệm), "investment" (tiền vào đầu tư)
- expense_category: chỉ cho expense - "food", "coffee", "transport", "shopping", "entertainment", "health", "education", "utilities", "other"
- amount: số tiền dương (không âm), đơn vị VND
- description: mô tả ngắn gọn về giao dịch
- date: ngày giao dịch format YYYY-MM-DD
- ai_confidence: độ tin cậy 0.0-1.0

Ví dụ response:
{
  "transaction_type": "expense", 
  "amount": 50000,
  "description": "Mua coffee Starbucks", 
  "date": "2024-01-15",
  "expense_category": "coffee",
  "ai_confidence": 0.95
}

Email cần phân tích:
""",
                'en': """
You are an AI specialized in analyzing TPBank transaction emails.
Task: Extract accurate transaction information from emails and return JSON.

Classification rules:
- transaction_type: "expense" (money out), "saving" (money in for saving), "investment" (money in for investment)
- expense_category: only for expense - "food", "coffee", "transport", "shopping", "entertainment", "health", "education", "utilities", "other"
- amount: positive amount (not negative), in VND
- description: brief description of transaction
- date: transaction date in YYYY-MM-DD format
- ai_confidence: confidence score 0.0-1.0

Example response:
{
  "transaction_type": "expense",
  "amount": 50000, 
  "description": "Coffee Starbucks purchase",
  "date": "2024-01-15",
  "expense_category": "coffee",
  "ai_confidence": 0.95
}

Email to analyze:
"""
            }
        }
    
    def parse_bank_email(self, email_content: str, bank_code: str, user_context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Parse bank email using Gemini AI
        
        Args:
            email_content: Full email content (subject + body)
            bank_code: Bank identifier (e.g., 'tpbank')
            user_context: Additional context like account suffix
            
        Returns:
            Parsed transaction data or None if parsing fails
        """
        try:
            # Get bank-specific prompt
            bank_prompts = self.bank_prompts.get(bank_code, {})
            if not bank_prompts:
                logger.error(f"No prompts found for bank: {bank_code}")
                return None
            
            # Select prompt by language
            prompt = bank_prompts.get(self.language, bank_prompts.get('vi'))
            if not prompt:
                logger.error(f"No prompt found for bank {bank_code} in language {self.language}")
                return None
            
            # Prepare full prompt with email content
            full_prompt = prompt + "\n\n" + email_content
            
            # Add user context if available
            if user_context:
                account_suffix = user_context.get('account_suffix')
                if account_suffix:
                    full_prompt += f"\n\nUser's account ends with: {account_suffix}"
            
            # Use existing GeminiService to get AI response
            ai_response = self.get_ai_response(full_prompt)
            
            if not ai_response:
                logger.warning(f"No AI response for bank email parsing")
                return None
            
            # Extract JSON from AI response
            parsed_data = self._extract_json_from_response(ai_response)
            
            if not parsed_data:
                logger.warning(f"Failed to extract JSON from AI response")
                return None
            
            # Validate and normalize parsed data
            validated_data = self._validate_transaction_data(parsed_data)
            
            if validated_data:
                logger.info(f"Successfully parsed bank email with confidence {validated_data.get('ai_confidence', 0)}")
                return validated_data
            else:
                logger.warning("Transaction data validation failed")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing bank email: {str(e)}")
            return None
    
    def _extract_json_from_response(self, ai_response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from AI response text"""
        try:
            # First try to find JSON between code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    # Try the entire response as JSON
                    json_str = ai_response.strip()
            
            # Parse JSON
            parsed_data = json.loads(json_str)
            
            # Basic structure validation
            if isinstance(parsed_data, dict):
                return parsed_data
            else:
                logger.warning(f"AI response is not a dictionary: {type(parsed_data)}")
                return None
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from AI response: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            return None
    
    def _validate_transaction_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and normalize transaction data"""
        try:
            # Required fields
            required_fields = ['transaction_type', 'amount', 'description', 'date']
            for field in required_fields:
                if field not in data or data[field] is None:
                    logger.warning(f"Missing required field: {field}")
                    return None
            
            # Validate transaction_type
            valid_types = ['expense', 'saving', 'investment']
            if data['transaction_type'] not in valid_types:
                logger.warning(f"Invalid transaction_type: {data['transaction_type']}")
                return None
            
            # Validate and convert amount
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    logger.warning(f"Invalid amount: {amount}")
                    return None
                data['amount'] = abs(amount)  # Ensure positive
            except (ValueError, TypeError):
                logger.warning(f"Invalid amount format: {data['amount']}")
                return None
            
            # Validate date format
            try:
                datetime.strptime(data['date'], '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid date format: {data['date']}")
                return None
            
            # Validate expense_category (only for expenses)
            if data['transaction_type'] == 'expense':
                valid_categories = [
                    'food', 'coffee', 'transport', 'shopping', 'entertainment',
                    'health', 'education', 'utilities', 'other'
                ]
                category = data.get('expense_category')
                if not category or category not in valid_categories:
                    # Default to 'other' if missing or invalid
                    data['expense_category'] = 'other'
                    logger.info(f"Set default expense_category to 'other'")
            else:
                # Remove expense_category for non-expense transactions
                data.pop('expense_category', None)
            
            # Validate confidence score
            confidence = data.get('ai_confidence', 0.5)
            try:
                confidence = float(confidence)
                confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
                data['ai_confidence'] = confidence
            except (ValueError, TypeError):
                data['ai_confidence'] = 0.5  # Default confidence
            
            # Ensure description is string and not empty
            description = str(data.get('description', '')).strip()
            if not description:
                logger.warning("Empty transaction description")
                return None
            data['description'] = description
            
            return data
            
        except Exception as e:
            logger.error(f"Error validating transaction data: {str(e)}")
            return None
    
    def parse_multiple_emails(self, emails: List[Dict[str, Any]], bank_code: str, user_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Parse multiple bank emails efficiently
        
        Args:
            emails: List of email dictionaries
            bank_code: Bank identifier
            user_context: User context for parsing
            
        Returns:
            List of successfully parsed transactions
        """
        parsed_transactions = []
        
        for email in emails:
            try:
                # Combine subject and body for parsing
                email_content = f"Subject: {email.get('subject', '')}\n\n{email.get('body', '')}"
                
                # Parse individual email
                parsed_transaction = self.parse_bank_email(email_content, bank_code, user_context)
                
                if parsed_transaction:
                    # Add email metadata
                    parsed_transaction['email_id'] = email.get('id')
                    parsed_transaction['email_date'] = email.get('date')
                    parsed_transaction['email_subject'] = email.get('subject', '')
                    
                    parsed_transactions.append(parsed_transaction)
                else:
                    logger.warning(f"Failed to parse email {email.get('id', 'unknown')}")
                    
            except Exception as e:
                logger.error(f"Error parsing email {email.get('id', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"Successfully parsed {len(parsed_transactions)} out of {len(emails)} emails")
        return parsed_transactions
    
    def test_parsing_with_sample(self, bank_code: str = 'tpbank') -> Dict[str, Any]:
        """
        Test parsing with sample email for validation
        
        Args:
            bank_code: Bank to test with
            
        Returns:
            Test result with parsed data
        """
        # Sample TPBank email content
        sample_email = """
Subject: Thông báo giao dịch - TPBank

Kính gửi Quý khách,

Tài khoản của Quý khách vừa có giao dịch như sau:

Thời gian: 15/01/2024 14:30:25
Loại giao dịch: Thanh toán
Số tiền: -50,000 VND
Số dư: 2,500,000 VND
Nội dung: Coffee Highlands *1234
Địa điểm: Highlands Coffee

Cảm ơn Quý khách đã sử dụng dịch vụ TPBank.
"""
        
        try:
            result = self.parse_bank_email(sample_email, bank_code)
            
            return {
                'success': result is not None,
                'parsed_data': result,
                'test_email': sample_email,
                'bank_code': bank_code
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'test_email': sample_email,
                'bank_code': bank_code
            } 