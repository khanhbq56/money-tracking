/**
 * Vietnamese translations
 */
const viTranslations = {
    'expense': 'Chi Tiêu',
    'saving': 'Tiết Kiệm', 
    'investment': 'Đầu Tư',
    'monthly_total': 'Tổng Tháng',
    'this_month': 'Tháng này',
    'net_amount': 'Số dư ròng',
    'send': 'Gửi',
    'today': 'Hôm Nay',
    'ai_assistant': 'AI Assistant',
    'enter_transaction': 'VD: coffee 25k, tiết kiệm 200k...',
    'welcome_message': 'Xin chào! Hãy nói cho tôi biết giao dịch của bạn. VD: "ăn trưa 50k"',
    'lunch': 'Ăn trưa',
    'quick_actions': 'Thao Tác Nhanh',
    'future_me': 'Future Me Simulator',
    'generate_meme': 'Tạo Meme',
    'statistics': 'Thống Kê',
    'today_total': 'Tổng hôm nay:',
    'all': 'Tất cả',
    'smart_financial_management': 'Quản lý tài chính thông minh',
    'calendar_coming_soon': 'Lịch sẽ được triển khai ở Phase 4',
    'calendar_description': 'Calendar tương tác với hiển thị giao dịch theo ngày',
    'online': 'Online',
    'tieng_viet': 'Tiếng Việt',
    'english': 'English',
    'expense_tracker': 'Theo Dõi Chi Tiêu',
    'financial_calendar': 'Lịch Tài Chính',
    'total_transactions': 'Tổng giao dịch',
    'transaction_details': 'Chi tiết giao dịch',
    'description': 'Mô tả',
    'amount': 'Số tiền',
    'type': 'Loại',
    'date': 'Ngày',
    'edit': 'Sửa',
    'delete': 'Xóa',
    'add_transaction': 'Thêm giao dịch',
    'save': 'Lưu',
    'cancel': 'Hủy',
    'close': 'Đóng',
    'add_first_transaction': 'Thêm giao dịch đầu tiên',
    'no_transactions_day': 'Chưa có giao dịch nào trong ngày này',
    'no_transactions_today': 'Chưa có giao dịch hôm nay',
    'description_placeholder': 'VD: ăn trưa, cafe...',
    'confidence': 'Độ tin cậy',
    'generate_new': 'Tạo mới',
    'share': 'Chia sẻ',
    'ai_analysis': 'Phân tích AI',
    'weekly_meme': 'Meme tuần',
    // Days of week
    'monday': 'Thứ 2',
    'tuesday': 'Thứ 3',
    'wednesday': 'Thứ 4',
    'thursday': 'Thứ 5',
    'friday': 'Thứ 6',
    'saturday': 'Thứ 7',
    'sunday': 'CN'
};

// Export for use in i18n.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = viTranslations;
} else {
    window.viTranslations = viTranslations;
} 