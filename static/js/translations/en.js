/**
 * English translations
 */
const enTranslations = {
    'expense': 'Expense',
    'saving': 'Saving',
    'investment': 'Investment', 
    'monthly_total': 'Monthly Total',
    'this_month': 'This month',
    'net_amount': 'Net amount',
    'send': 'Send',
    'today': 'Today',
    'ai_assistant': 'AI Assistant',
    'enter_transaction': 'e.g: coffee 25k, saving 200k...',
    'welcome_message': 'Hello! Tell me about your transaction. e.g: "lunch 50k"',
    'lunch': 'Lunch',
    'quick_actions': 'Quick Actions',
    'future_me': 'Future Me Simulator',
    'generate_meme': 'Generate Meme',
    'statistics': 'Statistics',
    'today_total': 'Today total:',
    'all': 'All',
    'smart_financial_management': 'Smart financial management',
    'calendar_coming_soon': 'Calendar will be implemented in Phase 4',
    'calendar_description': 'Interactive calendar with daily transaction display',
    'online': 'Online',
    'tieng_viet': 'Tiếng Việt',
    'english': 'English',
    'expense_tracker': 'Expense Tracker',
    'financial_calendar': 'Financial Calendar',
    'total_transactions': 'Total Transactions',
    'transaction_details': 'Transaction Details',
    'description': 'Description',
    'amount': 'Amount',
    'type': 'Type',
    'date': 'Date',
    'edit': 'Edit',
    'delete': 'Delete',
    'add_transaction': 'Add Transaction',
    'save': 'Save',
    'cancel': 'Cancel',
    'close': 'Close',
    'confirm': 'Confirm',
    'add_first_transaction': 'Add First Transaction',
    'no_transactions_day': 'No transactions for this day',
    'no_transactions_today': 'No transactions today',
    'description_placeholder': 'e.g: lunch, coffee...',
    'confidence': 'Confidence',
    'generate_new': 'Generate New',
    
    // Transaction messages
    'transaction_added_success': '✅ Transaction added successfully!',
    'transaction_updated_success': '✅ Transaction updated successfully!',
    'transaction_deleted_success': '✅ Transaction deleted successfully!',
    'transaction_confirm_success': '✅ Transaction confirmed successfully!',
    
    // Error messages
    'transaction_add_error': '❌ Error adding transaction. Please try again!',
    'transaction_update_error': '❌ Error updating transaction. Please try again!',
    'transaction_delete_error': '❌ Error deleting transaction. Please try again!',
    'transaction_confirm_error': '❌ Error confirming transaction. Please try again!',
    'error_occurred': 'Sorry, an error occurred. Please try again!',
    
    // Validation messages
    'validation_required_fields': '⚠️ Please fill in all required fields!',
    'validation_expense_category': '⚠️ Please select expense category!',
    
    // Confirmation messages
    'confirm_delete_transaction': 'Are you sure you want to delete this transaction?',
    
    // Chat edit message
    'chat_edit_help': '✏️ Please edit and send again!',
    'chat_analysis_message': 'I have analyzed your transaction:',
    
    // Transaction types display
    'transaction_type_expense': '🔴 Expense',
    'transaction_type_saving': '🟢 Saving',
    'transaction_type_investment': '🔵 Investment',
    'share': 'Share',
    'ai_analysis': 'AI Analysis',
    'weekly_meme': 'Weekly Meme',
    // Days of week
    'monday': 'Mon',
    'tuesday': 'Tue',
    'wednesday': 'Wed',
    'thursday': 'Thu',
    'friday': 'Fri',
    'saturday': 'Sat',
    'sunday': 'Sun',
    
    // Voice input
    'voice_listening': 'Listening...',
    'voice_input_tooltip': 'Voice Input (Ctrl+Shift+V)',
    'voice_not_supported': 'Browser does not support voice input. Please use Chrome or Edge.',
    'voice_no_speech': 'No speech detected. Please try again.',
    'voice_access_denied': 'Microphone access denied.',
    'voice_network_error': 'Network error. Check internet connection.',
    'voice_error': 'Voice recognition error. Please try again.',
    'voice_recorded_message': 'Recorded: "{transcript}". Press Send to process.',
    
    // Date formatting
    'date_today': 'today',
    'date_yesterday': 'yesterday',
    'date_day_before_yesterday': 'day before yesterday',
    'date_format': 'MM/dd/yyyy',
    'date_days_ago': '{days} days ago',
    'date_weeks_ago': '{weeks} weeks ago',
    
    // Category translations
    'category_food': 'Food & Drink',
    'category_transport': 'Transport',
    'category_saving': 'Saving',
    'category_investment': 'Investment',
    
    // Dialog titles
    'dialog_delete_transaction': 'Delete Transaction',
    'dialog_day_details': '📅 Day Details',
    'button_delete': 'Delete',
    'button_cancel': 'Cancel',
    'edit_transaction': 'Edit Transaction',
    'button_update': 'Update',
    
    // Alert dialog titles
    'error_title': 'Error',
    'success_title': 'Success',
    'notice_title': 'Notice'
};

// Export for use in i18n.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = enTranslations;
} else {
    window.enTranslations = enTranslations;
} 