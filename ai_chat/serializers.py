from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import ChatMessage
from transactions.serializers import TransactionSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ChatMessage model.
    """
    suggested_transaction = TransactionSerializer(read_only=True)
    voice_indicator = serializers.SerializerMethodField()
    status_indicator = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'user_message', 'ai_response', 'suggested_transaction',
            'is_confirmed', 'has_voice_input', 'voice_transcript',
            'parsed_date', 'language', 'created_at', 'voice_indicator',
            'status_indicator'
        ]
        read_only_fields = ['created_at']
    
    def get_voice_indicator(self, obj):
        """Get emoji indicator for voice input"""
        return "🎤" if obj.has_voice_input else "⌨️"
    
    def get_status_indicator(self, obj):
        """Get emoji indicator for confirmation status"""
        return "✅" if obj.is_confirmed else "⏳"


class ChatProcessRequestSerializer(serializers.Serializer):
    """
    Serializer for processing chat messages with AI.
    """
    message = serializers.CharField(
        max_length=1000,
        help_text=_('User message to process')
    )
    has_voice = serializers.BooleanField(
        default=False,
        help_text=_('Whether the message was inputted via voice')
    )
    language = serializers.ChoiceField(
        choices=[('vi', 'Vietnamese'), ('en', 'English')],
        default='vi',
        help_text=_('Language for processing')
    )
    
    def validate_message(self, value):
        """Validate that message is not empty"""
        if not value.strip():
            raise serializers.ValidationError(_('Message cannot be empty.'))
        return value.strip()


class ChatProcessResponseSerializer(serializers.Serializer):
    """
    Serializer for AI chat processing response.
    """
    chat_id = serializers.IntegerField(help_text=_('ID of the created chat message'))
    ai_result = serializers.DictField(help_text=_('AI analysis result'))
    suggested_text = serializers.CharField(help_text=_('Human-readable response text'))
    parsed_date = serializers.DateField(
        allow_null=True,
        help_text=_('Parsed date from the message')
    )
    confidence = serializers.FloatField(help_text=_('AI confidence score'))


class TransactionConfirmRequestSerializer(serializers.Serializer):
    """
    Serializer for confirming transactions from AI suggestions.
    """
    chat_id = serializers.IntegerField(help_text=_('ID of the chat message'))
    transaction_data = serializers.DictField(help_text=_('Transaction data to confirm'))
    custom_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text=_('Custom date for the transaction')
    )
    
    def validate_chat_id(self, value):
        """Validate that chat message exists"""
        try:
            ChatMessage.objects.get(id=value)
        except ChatMessage.DoesNotExist:
            raise serializers.ValidationError(_('Chat message not found.'))
        return value
    
    def validate_transaction_data(self, value):
        """Validate transaction data structure"""
        required_fields = ['type', 'amount', 'description']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(
                    _(f'Transaction data must include {field}.')
                )
        
        # Validate transaction type
        valid_types = ['expense', 'saving', 'investment']
        if value['type'] not in valid_types:
            raise serializers.ValidationError(
                _(f'Transaction type must be one of: {", ".join(valid_types)}')
            )
        
        # Validate amount
        try:
            amount = float(value['amount'])
            if amount <= 0:
                raise serializers.ValidationError(_('Amount must be greater than 0.'))
        except (ValueError, TypeError):
            raise serializers.ValidationError(_('Amount must be a valid number.'))
        
        return value


class TransactionConfirmResponseSerializer(serializers.Serializer):
    """
    Serializer for transaction confirmation response.
    """
    success = serializers.BooleanField(help_text=_('Whether the confirmation was successful'))
    transaction_id = serializers.IntegerField(
        allow_null=True,
        help_text=_('ID of the created transaction')
    )
    transaction_date = serializers.DateField(
        allow_null=True,
        help_text=_('Date of the transaction')
    )
    message = serializers.CharField(
        required=False,
        help_text=_('Success or error message')
    )


class TranslationResponseSerializer(serializers.Serializer):
    """
    Serializer for i18n translation responses.
    """
    language = serializers.CharField(help_text=_('Language code'))
    translations = serializers.DictField(help_text=_('Translation key-value pairs'))


class AIResultSerializer(serializers.Serializer):
    """
    Serializer for AI analysis results.
    """
    type = serializers.ChoiceField(
        choices=['expense', 'saving', 'investment'],
        help_text=_('Transaction type')
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=0,
        help_text=_('Transaction amount')
    )
    description = serializers.CharField(
        max_length=200,
        help_text=_('Transaction description')
    )
    category = serializers.CharField(
        required=False,
        allow_null=True,
        help_text=_('Expense category (only for expenses)')
    )
    confidence = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        help_text=_('AI confidence score')
    )
    icon = serializers.CharField(help_text=_('Transaction icon'))
    parsed_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text=_('Parsed date from message')
    )
    has_voice = serializers.BooleanField(
        default=False,
        help_text=_('Whether input was voice')
    ) 