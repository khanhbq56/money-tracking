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
from .voice_processor import VoiceProcessor
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
    
    # Import services
    from .gemini_service import GeminiService
    
    try:
        # Use enhanced voice processing if voice input
        if has_voice:
            voice_processor = VoiceProcessor(language)
            ai_result = voice_processor.process_voice_input(user_message, language)
        else:
            # Use regular Gemini service for text input
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


@api_view(['GET'])
def get_calendar_data(request, year, month):
    """Get calendar data for specific month with transaction summaries"""
    try:
        from transactions.models import Transaction
        from datetime import date, timedelta
        import calendar
        
        # Get all transactions for the month
        transactions = Transaction.objects.filter(
            date__year=year,
            date__month=month
        ).select_related().order_by('date')
        
        # Group transactions by date
        daily_data = {}
        for transaction in transactions:
            date_str = transaction.date.isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = {
                    'transactions': [],
                    'totals': {'expense': 0, 'saving': 0, 'investment': 0, 'net': 0}
                }
            
            # Add transaction data
            transaction_data = {
                'id': transaction.id,
                'type': transaction.transaction_type,
                'amount': float(transaction.amount),
                'description': transaction.description,
                'category': transaction.expense_category if transaction.transaction_type == 'expense' else None,
                'icon': transaction.get_icon(),
                'confidence': transaction.ai_confidence
            }
            daily_data[date_str]['transactions'].append(transaction_data)
            
            # Update daily totals
            if transaction.transaction_type == 'expense':
                daily_data[date_str]['totals']['expense'] += float(transaction.amount)
            elif transaction.transaction_type == 'saving':
                daily_data[date_str]['totals']['saving'] += float(transaction.amount)
            elif transaction.transaction_type == 'investment':
                daily_data[date_str]['totals']['investment'] += float(transaction.amount)
        
        # Calculate net totals for each day
        for date_str in daily_data:
            totals = daily_data[date_str]['totals']
            # Hiển thị chi tiêu là âm, nhưng net total là tổng của tất cả
            expense_display = -abs(totals['expense']) if totals['expense'] != 0 else 0
            totals['expense'] = expense_display
            totals['net'] = abs(totals['expense']) + totals['saving'] + totals['investment']
        
        # Get month info
        month_name = calendar.month_name[month]
        days_in_month = calendar.monthrange(year, month)[1]
        first_day_weekday = calendar.monthrange(year, month)[0]  # 0=Monday
        
        return Response({
            'year': year,
            'month': month,
            'month_name': month_name,
            'days_in_month': days_in_month,
            'first_day_weekday': first_day_weekday,
            'daily_data': daily_data,
            'total_transactions': transactions.count()
        })
        
    except Exception as e:
        logger.error(f"Error getting calendar data: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_daily_summary(request, date):
    """Get detailed summary for a specific date"""
    try:
        from transactions.models import Transaction
        from datetime import datetime
        
        # Parse date
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get transactions for the date
        transactions = Transaction.objects.filter(
            date=target_date
        ).order_by('created_at')
        
        # Build summary
        summary_data = {
            'date': date,
            'transactions': [],
            'totals': {'expense': 0, 'saving': 0, 'investment': 0, 'net': 0},
            'count': transactions.count()
        }
        
        for transaction in transactions:
            transaction_data = {
                'id': transaction.id,
                'type': transaction.transaction_type,
                'amount': float(transaction.amount),
                'description': transaction.description,
                'category': transaction.expense_category if transaction.transaction_type == 'expense' else None,
                'icon': transaction.get_icon(),
                'confidence': transaction.ai_confidence,
                'created_at': transaction.created_at.isoformat()
            }
            summary_data['transactions'].append(transaction_data)
            
            # Update totals
            if transaction.transaction_type == 'expense':
                summary_data['totals']['expense'] += float(transaction.amount)
            elif transaction.transaction_type == 'saving':
                summary_data['totals']['saving'] += float(transaction.amount)
            elif transaction.transaction_type == 'investment':
                summary_data['totals']['investment'] += float(transaction.amount)
        
        # Calculate net total and format expense as negative
        expense_display = -abs(summary_data['totals']['expense']) if summary_data['totals']['expense'] != 0 else 0
        summary_data['totals']['expense'] = expense_display
        summary_data['totals']['net'] = (
            abs(summary_data['totals']['expense']) + 
            summary_data['totals']['saving'] + 
            summary_data['totals']['investment']
        )
        
        return Response(summary_data)
        
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    except Exception as e:
        logger.error(f"Error getting daily summary: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_monthly_totals(request):
    """Get monthly totals for dashboard display"""
    try:
        from transactions.monthly_service import get_current_month_totals
        from datetime import datetime
        
        # Get current month totals
        totals = get_current_month_totals()
        
        # Format for display
        formatted_totals = {
            'expense': f"-{totals['expense']:,.0f}₫",
            'saving': f"+{totals['saving']:,.0f}₫",
            'investment': f"+{totals['investment']:,.0f}₫",
            'net_total': f"+{totals['net_total']:,.0f}₫"
        }
        
        return Response({
            'monthly_totals': totals,
            'formatted': formatted_totals,
            'month': datetime.now().month,
            'year': datetime.now().year
        })
        
    except Exception as e:
        logger.error(f"Error getting monthly totals: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_translations(request, language):
    """Get translation strings for i18n support"""
    try:
        from django.utils.translation import activate, gettext as _
        
        # Activate the requested language
        activate(language)
        
        # Common translations for the app
        translations = {
            # Calendar
            'calendar': _('Calendar'),
            'previous_month': _('Previous Month'),
            'next_month': _('Next Month'),
            'today': _('Today'),
            'this_month': _('This Month'),
            
            # Days of week
            'monday': _('Monday'),
            'tuesday': _('Tuesday'),
            'wednesday': _('Wednesday'),
            'thursday': _('Thursday'),
            'friday': _('Friday'),
            'saturday': _('Saturday'),
            'sunday': _('Sunday'),
            
            # Months
            'january': _('January'),
            'february': _('February'),
            'march': _('March'),
            'april': _('April'),
            'may': _('May'),
            'june': _('June'),
            'july': _('July'),
            'august': _('August'),
            'september': _('September'),
            'october': _('October'),
            'november': _('November'),
            'december': _('December'),
            
            # Transaction types
            'expense': _('Expense'),
            'saving': _('Saving'),
            'investment': _('Investment'),
            'net_amount': _('Net Amount'),
            'monthly_total': _('Monthly Total'),
            
            # Actions
            'send': _('Send'),
            'confirm': _('Confirm'),
            'cancel': _('Cancel'),
            'add_transaction': _('Add Transaction'),
            'voice_input': _('Voice Input'),
            
            # Status
            'loading': _('Loading...'),
            'error': _('Error'),
            'success': _('Success'),
            
            # Voice features
            'listening': _('Listening...'),
            'voice_input_tooltip': _('Voice Input (Ctrl+Shift+V)'),
            'speak_clearly': _('Please speak clearly'),
            
            # Filters
            'all': _('All'),
            'filter_expense': _('Expenses'),
            'filter_saving': _('Savings'),
            'filter_investment': _('Investments'),
            
            # Messages
            'no_transactions': _('No transactions for this day'),
            'transaction_added': _('Transaction added successfully'),
            'ai_processing': _('AI is processing your message...'),
            
            # Meme related (Phase 9)
            'weekly_meme': _('Weekly Meme'),
            'generate_meme': _('Generate Meme'),
            'generate_new': _('Generate New'),
            'share': _('Share'),
            'ai_analysis': _('AI Analysis'),
            'analyzing_spending': _('Analyzing your spending...'),
            'try_again': _('Please try again later!'),
        }
        
        return Response({
            'language': language,
            'translations': translations
        })
        
    except Exception as e:
        logger.error(f"Error getting translations: {e}")
        return Response({'error': str(e)}, status=500)

# =====================
# PHASE 9: MEME GENERATOR API ENDPOINTS
# =====================

@api_view(['GET'])
def generate_weekly_meme(request):
    """Generate a weekly meme based on user's spending patterns"""
    try:
        from .meme_generator import MemeGenerator
        from django.utils.translation import get_language
        
        # Get current language
        language = get_language() or 'vi'
        
        # Initialize meme generator
        meme_gen = MemeGenerator(language=language)
        
        # Generate meme data
        meme_data = meme_gen.generate_weekly_meme()
        
        logger.info(f"Generated meme with personality: {meme_data['personality']}")
        
        return Response(meme_data)
        
    except Exception as e:
        logger.error(f"Error generating weekly meme: {e}")
        return Response({
            'error': 'Failed to generate meme',
            'details': str(e)
        }, status=500)

@api_view(['GET'])
def get_meme_analysis(request):
    """Get detailed spending analysis for meme generation"""
    try:
        from .meme_generator import MemeGenerator
        from django.utils.translation import get_language
        
        # Get current language
        language = get_language() or 'vi'
        
        # Initialize meme generator
        meme_gen = MemeGenerator(language=language)
        
        # Get analysis data
        analysis_data = meme_gen.get_spending_analysis()
        
        return Response(analysis_data)
        
    except Exception as e:
        logger.error(f"Error getting meme analysis: {e}")
        return Response({
            'error': 'Failed to get analysis',
            'details': str(e)
        }, status=500)

@api_view(['POST'])
def share_meme(request):
    """Handle meme sharing functionality"""
    try:
        meme_data = request.data.get('meme_data')
        timestamp = request.data.get('timestamp')
        
        if not meme_data:
            return Response({'error': 'No meme data provided'}, status=400)
        
        # Log the share action (could be enhanced to save to database)
        logger.info(f"Meme shared - Personality: {meme_data.get('personality')}, Timestamp: {timestamp}")
        
        # Here you could add analytics tracking, social media integration, etc.
        
        return Response({
            'success': True,
            'message': 'Meme shared successfully',
            'share_url': request.build_absolute_uri('/'),
            'shareable_text': meme_data.get('shareable_text', 'Check out my expense tracker meme!')
        })
        
    except Exception as e:
        logger.error(f"Error sharing meme: {e}")
        return Response({
            'error': 'Failed to share meme',
            'details': str(e)
        }, status=500) 