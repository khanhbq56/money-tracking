from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.translation import gettext as _, get_language
from django.utils import timezone
from datetime import datetime, date
import json
import re
import logging

logger = logging.getLogger(__name__)

from .models import ChatMessage
from .serializers import (
    ChatMessageSerializer, ChatProcessRequestSerializer, ChatProcessResponseSerializer,
    TransactionConfirmRequestSerializer, TransactionConfirmResponseSerializer,
    TranslationResponseSerializer, AIResultSerializer
)
from transactions.models import Transaction
from transactions.monthly_service import update_monthly_totals_on_transaction_change


def placeholder_view(request):
    """Placeholder view for AI chat - will be implemented in Phase 5"""
    return JsonResponse({
        'status': 'Phase 1 Complete', 
        'message': 'AI Chat endpoints will be implemented in Phase 5'
    }) 


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ChatMessage CRUD operations.
    """
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    ordering = ['-created_at']


@api_view(['POST'])
def process_chat_message(request):
    """
    Process user chat message with AI analysis using Gemini.
    """
    serializer = ChatProcessRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"Invalid request data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_message = serializer.validated_data['message']
    has_voice = serializer.validated_data['has_voice']
    language = serializer.validated_data['language']
    
    logger.info(f"Processing chat message: '{user_message[:50]}...' (voice: {has_voice}, lang: {language})")
    
    # Import and use Gemini service
    from .gemini_service import GeminiService
    
    try:
        # Use Gemini service for AI processing
        gemini = GeminiService(language)
        ai_result = gemini.categorize_transaction(user_message, has_voice)
        
        # Save chat message
        chat_message = ChatMessage.objects.create(
            user_message=user_message,
            ai_response=json.dumps(ai_result),
            has_voice_input=has_voice,
            voice_transcript=user_message if has_voice else '',
            parsed_date=datetime.strptime(ai_result['parsed_date'], '%Y-%m-%d').date(),
            language=language
        )
        
        # Generate response text based on language
        response_text = _generate_response_text(ai_result, language)
        
        logger.info(f"Chat message processed successfully: ID {chat_message.id}")
        
        response_serializer = ChatProcessResponseSerializer({
            'chat_id': chat_message.id,
            'ai_result': ai_result,
            'suggested_text': response_text,
            'parsed_date': ai_result['parsed_date'],
            'confidence': ai_result['confidence']
        })
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        
        # Fallback to simple categorization on any error
        ai_result = _simple_categorization(user_message, language)
        ai_result['has_voice'] = has_voice
        ai_result['parsed_date'] = date.today().isoformat()
        
        chat_message = ChatMessage.objects.create(
            user_message=user_message,
            ai_response=json.dumps(ai_result),
            has_voice_input=has_voice,
            voice_transcript=user_message if has_voice else '',
            parsed_date=date.today(),
            language=language
        )
        
        response_text = _generate_response_text(ai_result, language)
        
        response_serializer = ChatProcessResponseSerializer({
            'chat_id': chat_message.id,
            'ai_result': ai_result,
            'suggested_text': response_text,
            'parsed_date': ai_result['parsed_date'],
            'confidence': ai_result['confidence']
        })
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def confirm_transaction(request):
    """
    Confirm and save transaction from AI suggestion.
    """
    serializer = TransactionConfirmRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    chat_id = serializer.validated_data['chat_id']
    transaction_data = serializer.validated_data['transaction_data']
    custom_date = serializer.validated_data.get('custom_date')
    
    try:
        # Get chat message
        chat_message = ChatMessage.objects.get(id=chat_id)
        
        # Determine transaction date
        if custom_date:
            transaction_date = custom_date
        elif chat_message.parsed_date:
            transaction_date = chat_message.parsed_date
        else:
            transaction_date = timezone.now().date()
        
        # Create transaction
        transaction = Transaction.objects.create(
            transaction_type=transaction_data['type'],
            amount=abs(float(transaction_data['amount'])),  # Model will handle sign
            description=transaction_data['description'],
            date=transaction_date,
            expense_category=transaction_data.get('category') if transaction_data['type'] == 'expense' else None,
            ai_confidence=transaction_data.get('confidence', 0.8)
        )
        
        # Update chat message
        chat_message.suggested_transaction = transaction
        chat_message.is_confirmed = True
        chat_message.save()
        
        # Update monthly totals
        update_monthly_totals_on_transaction_change(transaction)
        
        response_serializer = TransactionConfirmResponseSerializer({
            'success': True,
            'transaction_id': transaction.id,
            'transaction_date': transaction_date,
            'message': _('Transaction confirmed successfully')
        })
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except ChatMessage.DoesNotExist:
        return Response(
            {'error': _('Chat message not found')},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': _(f'Error creating transaction: {str(e)}')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_translations(request, language_code):
    """
    Get translation strings for the specified language.
    
    This is a stub implementation. Full i18n will be implemented in Phase 3.
    """
    # Stub translations
    translations = {
        'vi': {
            'expense': '🔴 Chi tiêu',
            'saving': '🟢 Tiết kiệm',
            'investment': '🔵 Đầu tư',
            'this_month': 'Tháng này',
            'today': 'Hôm nay',
            'send': 'Gửi',
            'ai_assistant': 'Trợ Lý AI',
            'enter_transaction': 'Nhập giao dịch',
            'monthly_total': 'Tổng Tháng',
            'net_amount': 'Số dư ròng',
            'future_me_simulator': 'Mô Phỏng Tương Lai',
            'generate_meme': 'Tạo Meme',
            'statistics': 'Thống Kê'
        },
        'en': {
            'expense': '🔴 Expense',
            'saving': '🟢 Saving',
            'investment': '🔵 Investment',
            'this_month': 'This Month',
            'today': 'Today',
            'send': 'Send',
            'ai_assistant': 'AI Assistant',
            'enter_transaction': 'Enter transaction',
            'monthly_total': 'Monthly Total',
            'net_amount': 'Net Amount',
            'future_me_simulator': 'Future Me Simulator',
            'generate_meme': 'Generate Meme',
            'statistics': 'Statistics'
        }
    }
    
    if language_code not in translations:
        return Response(
            {'error': _('Language not supported')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    response_serializer = TranslationResponseSerializer({
        'language': language_code,
        'translations': translations[language_code]
    })
    
    return Response(response_serializer.data)


def _simple_categorization(message, language='vi'):
    """
    Simple rule-based categorization for stub implementation.
    Will be replaced with Gemini AI in Phase 5.
    """
    message_lower = message.lower()
    
    # Extract amount using regex
    amount = _extract_amount(message)
    
    # Default values
    result = {
        'type': 'expense',
        'amount': amount,
        'description': message[:50],  # Truncate description
        'category': 'other',
        'confidence': 0.8,
        'icon': '📦'
    }
    
    # Pattern matching for Vietnamese
    if language == 'vi':
        if any(word in message_lower for word in ['coffee', 'cafe', 'cà phê']):
            result.update({
                'type': 'expense',
                'category': 'coffee',
                'description': 'Coffee',
                'icon': '☕'
            })
        elif any(word in message_lower for word in ['ăn', 'trưa', 'sáng', 'tối', 'phở', 'cơm']):
            result.update({
                'type': 'expense',
                'category': 'food',
                'description': 'Ăn uống',
                'icon': '🍜'
            })
        elif any(word in message_lower for word in ['grab', 'taxi', 'xe ôm', 'xăng']):
            result.update({
                'type': 'expense',
                'category': 'transport',
                'description': 'Di chuyển',
                'icon': '🚗'
            })
        elif any(word in message_lower for word in ['tiết kiệm', 'gửi ngân hàng', 'save']):
            result.update({
                'type': 'saving',
                'description': 'Tiết kiệm',
                'category': None,
                'icon': '💰'
            })
        elif any(word in message_lower for word in ['đầu tư', 'mua cổ phiếu', 'invest', 'bitcoin']):
            result.update({
                'type': 'investment',
                'description': 'Đầu tư',
                'category': None,
                'icon': '📈'
            })
    
    # English patterns
    elif language == 'en':
        if any(word in message_lower for word in ['coffee', 'cafe']):
            result.update({
                'type': 'expense',
                'category': 'coffee',
                'description': 'Coffee',
                'icon': '☕'
            })
        elif any(word in message_lower for word in ['lunch', 'dinner', 'food', 'eat']):
            result.update({
                'type': 'expense',
                'category': 'food',
                'description': 'Food',
                'icon': '🍜'
            })
        elif any(word in message_lower for word in ['transport', 'taxi', 'gas', 'fuel']):
            result.update({
                'type': 'expense',
                'category': 'transport',
                'description': 'Transport',
                'icon': '🚗'
            })
        elif any(word in message_lower for word in ['saving', 'save money', 'bank deposit']):
            result.update({
                'type': 'saving',
                'description': 'Saving',
                'category': None,
                'icon': '💰'
            })
        elif any(word in message_lower for word in ['investment', 'buy stocks', 'invest']):
            result.update({
                'type': 'investment',
                'description': 'Investment',
                'category': None,
                'icon': '📈'
            })
    
    return result


def _extract_amount(message):
    """Extract amount from message using regex patterns"""
    # Pattern for amounts like "25k", "1.5M", "100000"
    patterns = [
        r'(\d+(?:\.\d+)?)\s*k',  # 25k, 1.5k
        r'(\d+(?:\.\d+)?)\s*m',  # 1M, 2.5M
        r'(\d+(?:,\d+)*)',       # 100,000 or 100000
    ]
    
    message_lower = message.lower()
    
    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            amount_str = match.group(1).replace(',', '')
            amount = float(amount_str)
            
            # Convert based on suffix
            if 'k' in message_lower:
                amount *= 1000
            elif 'm' in message_lower:
                amount *= 1000000
            
            return int(amount)
    
    # Default amount if nothing found
    return 10000


def _generate_response_text(ai_result, language):
    """Generate human-readable response text based on AI result"""
    if language == 'vi':
        type_labels = {
            'expense': 'Chi tiêu',
            'saving': 'Tiết kiệm',
            'investment': 'Đầu tư'
        }
        return f"{ai_result['icon']} Phân loại: {type_labels[ai_result['type']]} - {ai_result['description']} ({ai_result['amount']:,.0f}₫)"
    else:
        type_labels = {
            'expense': 'Expense',
            'saving': 'Saving', 
            'investment': 'Investment'
        }
        return f"{ai_result['icon']} Classified as: {type_labels[ai_result['type']]} - {ai_result['description']} ({ai_result['amount']:,.0f}₫)" 