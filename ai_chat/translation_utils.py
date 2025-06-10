"""
Translation utilities for backend code
Provides centralized translation without if-else conditions
"""
from django.utils.translation import gettext as _


class TranslationKey:
    """Translation keys constants"""
    # Category names
    CATEGORY_FOOD = 'category_food'
    CATEGORY_COFFEE = 'category_coffee'
    CATEGORY_TRANSPORT = 'category_transport'
    CATEGORY_SHOPPING = 'category_shopping'
    CATEGORY_ENTERTAINMENT = 'category_entertainment'
    CATEGORY_HEALTH = 'category_health'
    CATEGORY_EDUCATION = 'category_education'
    CATEGORY_UTILITIES = 'category_utilities'
    CATEGORY_OTHER = 'category_other'
    CATEGORY_SAVING = 'category_saving'
    CATEGORY_INVESTMENT = 'category_investment'
    
    # Date descriptions
    DATE_TODAY = 'date_today'
    DATE_YESTERDAY = 'date_yesterday'
    DATE_DAY_BEFORE_YESTERDAY = 'date_day_before_yesterday'
    DATE_DAYS_AGO = 'date_days_ago'
    DATE_WEEKS_AGO = 'date_weeks_ago'
    
    # Voice messages
    VOICE_SPEAK_CLEARLY = 'voice_speak_clearly'
    VOICE_NO_AMOUNT = 'voice_no_amount'
    VOICE_UNCLEAR_TYPE = 'voice_unclear_type'
    
    # Error messages
    ERROR_LANGUAGE_NOT_SUPPORTED = 'error_language_not_supported'
    
    # Transaction types
    TYPE_EXPENSE = 'transaction_type_expense'
    TYPE_SAVING = 'transaction_type_saving'
    TYPE_INVESTMENT = 'transaction_type_investment'


class BackendTranslator:
    """
    Backend translator that uses Django's translation system
    Replaces if-else language conditions
    """
    
    def __init__(self, language='vi'):
        self.language = language
        
    def get_category_name(self, category_key: str) -> str:
        """Get translated category name"""
        # Use Django's translation system
        return _(category_key)
    
    def get_date_description(self, date_key: str, **params) -> str:
        """Get translated date description with parameters"""
        translated = _(date_key)
        
        # Replace parameters if provided
        if params:
            for key, value in params.items():
                translated = translated.replace(f'{{{key}}}', str(value))
                
        return translated
    
    def get_voice_message(self, voice_key: str) -> str:
        """Get translated voice message"""
        return _(voice_key)
    
    def get_error_message(self, error_key: str) -> str:
        """Get translated error message"""
        return _(error_key)


# Translation mappings for different contexts
CATEGORY_TRANSLATIONS = {
    'food': TranslationKey.CATEGORY_FOOD,
    'coffee': TranslationKey.CATEGORY_COFFEE,
    'transport': TranslationKey.CATEGORY_TRANSPORT,
    'shopping': TranslationKey.CATEGORY_SHOPPING,
    'entertainment': TranslationKey.CATEGORY_ENTERTAINMENT,
    'health': TranslationKey.CATEGORY_HEALTH,
    'education': TranslationKey.CATEGORY_EDUCATION,
    'utilities': TranslationKey.CATEGORY_UTILITIES,
    'other': TranslationKey.CATEGORY_OTHER,
    'saving': TranslationKey.CATEGORY_SAVING,
    'investment': TranslationKey.CATEGORY_INVESTMENT,
}

# Transaction type translations
TYPE_TRANSLATIONS = {
    'expense': TranslationKey.TYPE_EXPENSE,
    'saving': TranslationKey.TYPE_SAVING,
    'investment': TranslationKey.TYPE_INVESTMENT,
}


def get_category_display_name(category_code: str, language: str = 'vi') -> str:
    """
    Get display name for category using translation system
    Replaces hardcoded if-else language conditions
    """
    translator = BackendTranslator(language)
    
    if category_code in CATEGORY_TRANSLATIONS:
        key = CATEGORY_TRANSLATIONS[category_code]
        return translator.get_category_name(key)
    
    # Fallback to code if not found
    return category_code.title()


def get_type_display_name(type_code: str, language: str = 'vi') -> str:
    """
    Get display name for transaction type using translation system
    """
    translator = BackendTranslator(language)
    
    if type_code in TYPE_TRANSLATIONS:
        key = TYPE_TRANSLATIONS[type_code]
        return translator.get_category_name(key)
    
    # Fallback to code if not found
    return type_code.title()


def format_date_description(days_diff: int, language: str = 'vi') -> str:
    """
    Format relative date description using translation system
    Replaces if-else language conditions
    """
    translator = BackendTranslator(language)
    
    if days_diff == 0:
        return translator.get_date_description(TranslationKey.DATE_TODAY)
    elif days_diff == 1:
        return translator.get_date_description(TranslationKey.DATE_YESTERDAY)
    elif days_diff == 2:
        return translator.get_date_description(TranslationKey.DATE_DAY_BEFORE_YESTERDAY)
    elif days_diff < 7:
        return translator.get_date_description(TranslationKey.DATE_DAYS_AGO, days=days_diff)
    elif days_diff < 30:
        weeks = days_diff // 7
        return translator.get_date_description(TranslationKey.DATE_WEEKS_AGO, weeks=weeks)
    else:
        # Return formatted date for older dates
        return None  # Let caller handle with date formatting


def get_voice_suggestion(suggestion_type: str, language: str = 'vi') -> str:
    """
    Get voice input suggestion using translation system
    """
    translator = BackendTranslator(language)
    
    suggestion_keys = {
        'speak_clearly': TranslationKey.VOICE_SPEAK_CLEARLY,
        'no_amount': TranslationKey.VOICE_NO_AMOUNT,
        'unclear_type': TranslationKey.VOICE_UNCLEAR_TYPE,
    }
    
    if suggestion_type in suggestion_keys:
        return translator.get_voice_message(suggestion_keys[suggestion_type])
    
    return '' 