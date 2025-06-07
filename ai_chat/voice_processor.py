import re
import logging
from typing import Dict, Any, Optional
from .date_parser import DateParser
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)


class VoiceProcessor:
    """
    Enhanced processor for voice input with better context awareness
    """
    
    def __init__(self, language='vi'):
        self.language = language
        self.date_parser = DateParser(language)
        self.gemini_service = GeminiService(language)
        
    def process_voice_input(self, transcript: str, language: str = None) -> Dict[str, Any]:
        """
        Process voice input with enhanced accuracy for spoken language
        
        Args:
            transcript: The voice transcript text
            language: Optional language override
            
        Returns:
            Processed transaction data with enhanced voice-specific handling
        """
        if language:
            self.language = language
            self.date_parser.language = language
            self.gemini_service.language = language
        
        # Clean and normalize transcript
        cleaned_transcript = self._clean_voice_transcript(transcript)
        
        # Parse date from voice input
        parsed_date = self.date_parser.parse_date_from_message(cleaned_transcript)
        
        # Process with Gemini (voice-aware)
        result = self.gemini_service.categorize_transaction(
            cleaned_transcript, 
            has_voice=True
        )
        
        # Enhance result with voice-specific processing
        enhanced_result = self._enhance_voice_result(result, cleaned_transcript, parsed_date)
        
        return enhanced_result
    
    def _clean_voice_transcript(self, transcript: str) -> str:
        """Clean and normalize voice transcript for better processing"""
        
        if not transcript:
            return ""
        
        # Convert to lowercase for processing
        cleaned = transcript.lower().strip()
        
        # Common voice recognition corrections for Vietnamese
        if self.language == 'vi':
            voice_corrections = {
                # Number corrections
                'hai mươi lăm': '25',
                'hai mươi năm': '25', 
                'năm mười': '50',
                'một trăm': '100',
                'hai trăm': '200',
                'ba trăm': '300',
                'năm trăm': '500',
                
                # Common phrase corrections
                'cà phê': 'coffee',
                'cafe': 'coffee',
                'uống cà phê': 'coffee',
                'mua cà phê': 'coffee',
                
                # Food corrections
                'ăn sáng': 'ăn sáng',
                'ăn trưa': 'ăn trưa', 
                'ăn tối': 'ăn tối',
                'ăn cơm': 'ăn cơm',
                'ăn phở': 'phở',
                
                # Transport corrections
                'đi taxi': 'taxi',
                'đi grab': 'grab',
                'đổ xăng': 'xăng',
                'tiền xăng': 'xăng',
                
                # Money corrections
                'nghìn đồng': 'k',
                'nghìn': 'k',
                'triệu đồng': 'M',
                'triệu': 'M',
                'đồng': '',
                
                # Date corrections  
                'hôm nay': 'hôm nay',
                'hôm qua': 'hôm qua',
                'ngày hôm qua': 'hôm qua',
                'ngày hôm nay': 'hôm nay',
            }
        else:
            # English voice corrections
            voice_corrections = {
                # Number corrections
                'twenty five': '25',
                'fifty': '50',
                'one hundred': '100',
                'two hundred': '200',
                
                # Money corrections
                'thousand': 'k',
                'million': 'M',
                'dollars': '',
                'dollar': '',
                
                # Common phrases
                'bought coffee': 'coffee',
                'had lunch': 'lunch',
                'had dinner': 'dinner',
                'took taxi': 'taxi',
                'gas money': 'gas',
                'fuel': 'gas',
            }
        
        # Apply corrections
        for wrong, correct in voice_corrections.items():
            cleaned = cleaned.replace(wrong, correct)
        
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _enhance_voice_result(self, result: Dict[str, Any], transcript: str, parsed_date) -> Dict[str, Any]:
        """Enhance the result with voice-specific improvements"""
        
        # Add voice metadata
        result['voice_metadata'] = {
            'original_transcript': transcript,
            'cleaned_transcript': self._clean_voice_transcript(transcript),
            'parsed_date': parsed_date.isoformat(),
            'date_description': self.date_parser.get_relative_description(parsed_date),
            'confidence_boost': 0.1  # Boost confidence for voice input
        }
        
        # Boost confidence for voice input (people are usually more intentional with voice)
        if 'confidence' in result:
            result['confidence'] = min(1.0, result['confidence'] + 0.1)
        
        # Enhance description with date context if not today
        if parsed_date != self.date_parser.today:
            date_desc = self.date_parser.get_relative_description(parsed_date)
            if self.language == 'vi':
                result['description'] = f"{result.get('description', '')} ({date_desc})"
            else:
                result['description'] = f"{result.get('description', '')} ({date_desc})"
        
        # Voice-specific amount corrections
        result = self._correct_voice_amounts(result, transcript)
        
        return result
    
    def _correct_voice_amounts(self, result: Dict[str, Any], transcript: str) -> Dict[str, Any]:
        """Apply voice-specific amount corrections"""
        
        transcript_lower = transcript.lower()
        
        # Common voice amount patterns
        if self.language == 'vi':
            # Check for common Vietnamese amount patterns
            amount_patterns = [
                (r'(\d+)\s*nghìn', lambda m: int(m.group(1)) * 1000),
                (r'(\d+)\s*triệu', lambda m: int(m.group(1)) * 1000000),
                (r'(\d+)\s*k', lambda m: int(m.group(1)) * 1000),
                (r'(\d+)\s*m', lambda m: int(m.group(1)) * 1000000),
            ]
        else:
            # English amount patterns
            amount_patterns = [
                (r'(\d+)\s*thousand', lambda m: int(m.group(1)) * 1000),
                (r'(\d+)\s*million', lambda m: int(m.group(1)) * 1000000),
                (r'(\d+)\s*k', lambda m: int(m.group(1)) * 1000),
                (r'(\d+)\s*m', lambda m: int(m.group(1)) * 1000000),
            ]
        
        # Try to extract amount with voice patterns
        for pattern, converter in amount_patterns:
            match = re.search(pattern, transcript_lower)
            if match:
                try:
                    corrected_amount = converter(match)
                    # Only apply if it's different and seems reasonable
                    current_amount = result.get('amount', 0)
                    if corrected_amount != current_amount and corrected_amount > 0:
                        result['amount'] = corrected_amount
                        result['voice_metadata']['amount_corrected'] = True
                        break
                except (ValueError, IndexError):
                    continue
        
        return result
    
    def suggest_voice_improvements(self, transcript: str) -> Dict[str, Any]:
        """Suggest improvements for voice input quality"""
        
        suggestions = {
            'clarity_score': self._calculate_clarity_score(transcript),
            'suggestions': [],
            'detected_issues': []
        }
        
        transcript_lower = transcript.lower()
        
        # Check for common voice recognition issues
        if len(transcript) < 5:
            suggestions['detected_issues'].append('transcript_too_short')
            if self.language == 'vi':
                suggestions['suggestions'].append('Hãy nói rõ hơn, ví dụ: "coffee hai mười lăm nghìn"')
            else:
                suggestions['suggestions'].append('Please speak more clearly, e.g.: "coffee twenty five thousand"')
        
        # Check for unclear amounts
        if not re.search(r'\d+', transcript):
            suggestions['detected_issues'].append('no_amount_detected')
            if self.language == 'vi':
                suggestions['suggestions'].append('Không tìm thấy số tiền. Hãy nói rõ số tiền, ví dụ: "25k" hoặc "hai mười lăm nghìn"')
            else:
                suggestions['suggestions'].append('No amount detected. Please specify the amount, e.g.: "25k" or "twenty five thousand"')
        
        # Check for unclear transaction type
        common_keywords = {
            'vi': ['coffee', 'ăn', 'trưa', 'sáng', 'tối', 'tiết kiệm', 'taxi', 'grab', 'xăng', 'mua'],
            'en': ['coffee', 'lunch', 'dinner', 'breakfast', 'saving', 'taxi', 'gas', 'buy']
        }
        
        keywords = common_keywords.get(self.language, common_keywords['vi'])
        if not any(keyword in transcript_lower for keyword in keywords):
            suggestions['detected_issues'].append('unclear_transaction_type')
            if self.language == 'vi':
                suggestions['suggestions'].append('Loại giao dịch không rõ. Hãy thêm từ khóa như "coffee", "ăn trưa", "tiết kiệm"')
            else:
                suggestions['suggestions'].append('Transaction type unclear. Please add keywords like "coffee", "lunch", "saving"')
        
        return suggestions
    
    def _calculate_clarity_score(self, transcript: str) -> float:
        """Calculate a clarity score for the voice transcript"""
        
        if not transcript:
            return 0.0
        
        score = 0.0
        max_score = 10.0
        
        # Length score (reasonable length)
        if 5 <= len(transcript) <= 50:
            score += 2.0
        elif len(transcript) > 50:
            score += 1.0
        
        # Contains numbers
        if re.search(r'\d+', transcript):
            score += 2.0
        
        # Contains common keywords
        common_keywords = {
            'vi': ['coffee', 'ăn', 'trưa', 'tiết kiệm', 'taxi', 'k', 'nghìn'],
            'en': ['coffee', 'lunch', 'saving', 'taxi', 'k', 'thousand']
        }
        
        keywords = common_keywords.get(self.language, common_keywords['vi'])
        keyword_count = sum(1 for keyword in keywords if keyword in transcript.lower())
        score += min(3.0, keyword_count * 1.0)
        
        # No excessive repetition
        words = transcript.lower().split()
        unique_words = set(words)
        if len(words) > 0:
            repetition_ratio = len(unique_words) / len(words)
            if repetition_ratio > 0.8:
                score += 2.0
            elif repetition_ratio > 0.6:
                score += 1.0
        
        # Grammar/structure score (simple check)
        if any(char in transcript for char in '.,!?'):
            score += 1.0
        
        return min(max_score, score) / max_score 