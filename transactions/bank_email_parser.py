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
QUAN TRỌNG: Bạn PHẢI chỉ trả về JSON hợp lệ, không được thêm bất kỳ text nào khác.

Bạn là AI chuyên phân tích email giao dịch ngân hàng TPBank. 
Nhiệm vụ: Trích xuất thông tin giao dịch từ email và CHỈ trả về JSON.

Quy tắc phân loại:
- transaction_type: "expense" (tiền ra), "saving" (tiền vào), "investment" (đầu tư)
- expense_category: chỉ cho expense - "food", "coffee", "transport", "shopping", "entertainment", "health", "education", "utilities", "other"
- amount: số tiền dương (QUAN TRỌNG: GIỮ NGUYÊN SỐ TIỀN THỰC TẾ TRONG EMAIL)
- currency: "USD" hoặc "VND" (dựa trên email content)
- description: mô tả ngắn gọn, PHẢI bao gồm tên merchant/cửa hàng nếu có
- date: ngày giao dịch YYYY-MM-DD
- ai_confidence: độ tin cậy 0.0-1.0

QUAN TRỌNG VỀ TIỀN TỆ - LUẬT XÁC ĐỊNH CHÍNH XÁC:

1. MERCHANT NƯỚC NGOÀI = USD (LUÔN LUÔN):
   * Supercell, Steam, Epic Games, Google Pay/Play, Apple, Amazon, Netflix, Spotify, PayPal
   * Bất kỳ tên có: SUPERCELLSTORE, FS *SUPERCELL, AMZN, PAYPAL, APPLE.COM, GOOGLE, STEAM
   * MọI merchant nước ngoài → currency: "USD" (KHÔNG QUAN TÂM SỐ TIỀN)

2. MERCHANT VIỆT NAM = VND:
   * SHOPEEPAY, GRABPAY, MOMO, ZALOPAY, các cửa hàng Việt Nam
   * Loại trừ: tên ngân hàng (TPBANK, VIETCOMBANK) - chỉ là người gửi email

3. NHẬN DIỆN TIỀN TỆ TỪ CÚ PHÁP:
   * "Giá trị giao dịch: [số] USD" hoặc "[số]USD" → currency: "USD"
   * "Giá trị giao dịch: [số] VND" hoặc "[số]VND" → currency: "VND"
   * BỎ QUA "số dư" (luôn là VND ở Việt Nam)

4. QUY TẮC SỐ TIỀN NHỎ:
   * Nếu merchant nước ngoài + số tiền < 500 → MỘT CÁI CHẮC CHẮN là USD
   * Ví dụ: "FS *SUPERCELLSTORE" với "11" → currency: "USD", amount: 11

MẶC ĐỊNH CUỐI CÙNG: currency: "VND"

- GIỮ NGUYÊN số tiền thực tế từ email, KHÔNG chuyển đổi

CHỈ trả về JSON như ví dụ:
{
  "transaction_type": "expense", 
  "amount": 70.50,
  "currency": "USD",
  "description": "Amazon payment", 
  "date": "2024-05-27",
  "expense_category": "shopping",
  "ai_confidence": 0.95
}

Hoặc:
{
  "transaction_type": "expense", 
  "amount": 150000,
  "currency": "VND",
  "description": "Thanh toán SHOPEEPAY", 
  "date": "2024-05-27",
  "expense_category": "shopping",
  "ai_confidence": 0.95
}

Email:
""",
                'en': """
IMPORTANT: You MUST return ONLY valid JSON, no additional text.

You are an AI specialized in analyzing TPBank transaction emails.
Task: Extract transaction information from emails and return ONLY JSON.

Classification rules:
- transaction_type: "expense" (money out), "saving" (money in), "investment" (investment)
- expense_category: only for expense - "food", "coffee", "transport", "shopping", "entertainment", "health", "education", "utilities", "other"
- amount: positive amount (IMPORTANT: PRESERVE EXACT AMOUNT FROM EMAIL)
- currency: "USD" or "VND" (based on email content)
- description: brief description, MUST include merchant name if available
- date: transaction date YYYY-MM-DD
- ai_confidence: confidence score 0.0-1.0

CURRENCY DETECTION RULES - PRECISE DETERMINATION:

1. FOREIGN MERCHANTS = USD (ALWAYS):
   * Supercell, Steam, Epic Games, Google Pay/Play, Apple, Amazon, Netflix, Spotify, PayPal
   * Any name containing: SUPERCELLSTORE, FS *SUPERCELL, AMZN, PAYPAL, APPLE.COM, GOOGLE, STEAM
   * ALL foreign merchants → currency: "USD" (IGNORE AMOUNT SIZE)

2. VIETNAMESE MERCHANTS = VND:
   * SHOPEEPAY, GRABPAY, MOMO, ZALOPAY, Vietnamese stores
   * Exclude: bank names (TPBANK, VIETCOMBANK) - just email senders

3. CURRENCY FROM SYNTAX:
   * "Transaction amount: [number] USD" or "[number]USD" → currency: "USD"
   * "Transaction amount: [number] VND" or "[number]VND" → currency: "VND"
   * IGNORE "balance" (always VND in Vietnam)

4. SMALL AMOUNT RULE:
   * If foreign merchant + amount < 500 → DEFINITELY USD
   * Example: "FS *SUPERCELLSTORE" with "11" → currency: "USD", amount: 11

FINAL DEFAULT: currency: "VND"

- PRESERVE the exact amount from email, DO NOT convert

Return ONLY JSON like this example:
{
  "transaction_type": "expense",
  "amount": 70.50,
  "currency": "USD",
  "description": "Amazon payment",
  "date": "2024-05-27",
  "expense_category": "shopping",
  "ai_confidence": 0.95
}

Or:
{
  "transaction_type": "expense",
  "amount": 150000,
  "currency": "VND", 
  "description": "SHOPEEPAY payment",
  "date": "2024-05-27",
  "expense_category": "shopping",
  "ai_confidence": 0.95
}

Email:
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
        logger.info(f"🤖 Parsing email for {bank_code}")
        
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
            
            # Use Gemini model to get AI response
            if not self.model:
                logger.warning("Gemini model not available")
                return None
            
            try:
                response = self.model.generate_content(full_prompt)
                ai_response = response.text.strip() if response and response.text else ""
                
                if not ai_response:
                    logger.warning(f"Empty AI response for bank email parsing")
                    return None
                
            except Exception as e:
                logger.error(f"Error calling Gemini API: {str(e)}")
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
        """Extract JSON from AI response text with improved debugging"""
        try:
            logger.info(f"Extracting JSON from response: {ai_response[:500]}...")
            
            # Clean the response
            cleaned_response = ai_response.strip()
            
            # First try to find JSON between code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                logger.info("Found JSON in code blocks")
            else:
                # Try to find JSON in the response
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    logger.info("Found JSON pattern in response")
                else:
                    # Try the entire response as JSON
                    json_str = cleaned_response
                    logger.info("Using entire response as JSON")
            
            # Log the JSON string being parsed
            logger.info(f"Attempting to parse JSON: {json_str[:300]}...")
            
            # Parse JSON
            parsed_data = json.loads(json_str)
            
            # Basic structure validation
            if isinstance(parsed_data, dict):
                logger.info(f"Successfully parsed JSON: {list(parsed_data.keys())}")
                return parsed_data
            else:
                logger.warning(f"AI response is not a dictionary: {type(parsed_data)}")
                return None
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from AI response: {str(e)}")
            logger.warning(f"Response that failed to parse: {ai_response[:200]}...")
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            return None
    
    def _validate_transaction_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and normalize transaction data with currency support"""
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
            
            # Validate currency field
            currency = data.get('currency', 'VND')  # Default to VND if not specified
            valid_currencies = ['USD', 'VND']
            if currency not in valid_currencies:
                logger.warning(f"Invalid currency: {currency}, defaulting to VND")
                currency = 'VND'
            data['currency'] = currency
            
            # Validate and convert amount with more flexibility
            try:
                amount = float(data['amount'])
                if amount < 0:
                    logger.warning(f"Negative amount: {amount}, converting to positive")
                    amount = abs(amount)
                elif amount == 0:
                    # AI couldn't find transaction info - set reasonable defaults
                    if currency == 'USD':
                        amount = 1.0  # $1 USD
                        logger.info("AI found no clear amount, using minimum $1 USD")
                    else:
                        amount = 1000  # 1000 VND
                        logger.info("AI found no clear amount, using minimum 1000 VND")
                data['amount'] = abs(amount)  # Ensure positive
            except (ValueError, TypeError):
                logger.warning(f"Invalid amount format: {data['amount']}, using default")
                if currency == 'USD':
                    data['amount'] = 1.0  # Default $1 USD
                else:
                    data['amount'] = 1000  # Default 1000 VND
            
            # Validate date format with fallback
            try:
                datetime.strptime(data['date'], '%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid date format: {data['date']}, using today's date")
                from datetime import date
                data['date'] = date.today().strftime('%Y-%m-%d')
            
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
            
            # Ensure description is string and provide fallback
            description = str(data.get('description', '')).strip()
            if not description:
                logger.warning("Empty transaction description, using fallback")
                description = "Giao dịch từ email ngân hàng"
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