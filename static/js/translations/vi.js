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
    'confirm': 'Xác nhận',
    'add_first_transaction': 'Thêm giao dịch đầu tiên',
    'no_transactions_day': 'Chưa có giao dịch nào trong ngày này',
    'no_transactions_today': 'Chưa có giao dịch hôm nay',
    'description_placeholder': 'VD: ăn trưa, cafe...',
    'confidence': 'Độ tin cậy',
    'generate_new': 'Tạo mới',
    
    // Transaction messages
    'transaction_added_success': '✅ Đã thêm giao dịch thành công!',
    'transaction_updated_success': '✅ Đã cập nhật giao dịch thành công!',
    'transaction_deleted_success': '✅ Đã xóa giao dịch thành công!',
    'transaction_confirm_success': '✅ Đã xác nhận giao dịch thành công!',
    
    // Error messages
    'transaction_add_error': '❌ Lỗi khi thêm giao dịch. Vui lòng thử lại!',
    'transaction_update_error': '❌ Lỗi khi cập nhật giao dịch. Vui lòng thử lại!',
    'transaction_delete_error': '❌ Lỗi khi xóa giao dịch. Vui lòng thử lại!',
    'transaction_confirm_error': '❌ Lỗi khi xác nhận giao dịch. Vui lòng thử lại!',
    'error_occurred': 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại!',
    
    // Validation messages
    'validation_required_fields': '⚠️ Vui lòng điền đầy đủ thông tin!',
    'validation_expense_category': '⚠️ Vui lòng chọn danh mục chi tiêu!',
    
    // Confirmation messages
    'confirm_delete_transaction': 'Bạn có chắc chắn muốn xóa giao dịch này?',
    
    // Chat edit message
    'chat_edit_help': '✏️ Hãy chỉnh sửa và gửi lại!',
    'chat_analysis_message': 'Tôi đã phân tích thông tin giao dịch của bạn:',
    
    // Transaction types display
    'transaction_type_expense': '🔴 Chi tiêu',
    'transaction_type_saving': '🟢 Tiết kiệm', 
    'transaction_type_investment': '🔵 Đầu tư',
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
    'sunday': 'CN',
    
    // Voice input
    'voice_listening': 'Đang nghe...',
    'voice_input_tooltip': 'Nhập bằng giọng nói (Ctrl+Shift+V)',
    'voice_not_supported': 'Trình duyệt không hỗ trợ nhập bằng giọng nói. Vui lòng sử dụng Chrome hoặc Edge.',
    'voice_no_speech': 'Không phát hiện giọng nói. Vui lòng thử lại.',
    'voice_access_denied': 'Quyền truy cập microphone bị từ chối.',
    'voice_network_error': 'Lỗi mạng. Kiểm tra kết nối internet.',
    'voice_error': 'Lỗi nhận dạng giọng nói. Vui lòng thử lại.',
    'voice_recorded_message': 'Đã ghi nhận: "{transcript}". Nhấn Gửi để xử lý.',
    
    // Date formatting
    'date_today': 'hôm nay',
    'date_yesterday': 'hôm qua',
    'date_day_before_yesterday': 'hôm kia',
    'date_format': 'dd/MM/yyyy',
    'date_days_ago': '{days} ngày trước',
    'date_weeks_ago': '{weeks} tuần trước',
    
    // Category translations
    'category_food': 'Ăn uống',
    'category_transport': 'Di chuyển',
    'category_saving': 'Tiết kiệm',
    'category_investment': 'Đầu tư',
    
    // Dialog titles
    'dialog_delete_transaction': 'Xóa giao dịch',
    'dialog_day_details': '📅 Chi tiết ngày',
    'button_delete': 'Xóa',
    'button_cancel': 'Hủy',
    'edit_transaction': 'Sửa giao dịch',
    'button_update': 'Cập nhật',
    
    // Alert dialog titles
    'error_title': 'Lỗi',
    'success_title': 'Thành công', 
    'notice_title': 'Thông báo'
};

// Export for use in i18n.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = viTranslations;
} else {
    window.viTranslations = viTranslations;
} 