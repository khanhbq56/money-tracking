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
    'notice_title': 'Thông báo',
    
    // Sample messages for quick actions
    'coffee_sample': 'coffee 25k',
    'lunch_sample': 'ăn trưa 50k',
    'saving_sample': 'tiết kiệm 200k',
    
    // Future Me Simulator
    'future_me_subtitle': 'Dự báo tài chính thông minh dựa trên dữ liệu thực',
    'analyzing_financial_data': 'Đang phân tích dữ liệu tài chính...',
    'please_wait': 'Vui lòng chờ trong giây lát',
    'select_forecast_period': 'Chọn khoảng thời gian dự báo',
    'one_month': '1 tháng',
    'five_years': '5 năm',
    'months': 'tháng',
    'years': 'năm',
    'expected_expense': 'Chi Tiêu Dự Kiến',
    'expected_saving': 'Tiết Kiệm Dự Kiến',
    'expected_investment': 'Đầu Tư Dự Kiến',
    'expected_total': 'Tổng Dự Kiến',
    'scenarios_what_if': 'Scenarios "What if" - Các kịch bản tối ưu',
    'goal_calculator': 'Goal Calculator - Máy tính mục tiêu',
    'goal_calculator_desc': 'Với tốc độ tiết kiệm hiện tại, bạn có thể đạt được:',
    'error_occurred_title': 'Oops! Có lỗi xảy ra',
    'try_again': 'Thử lại',
    'check_connection': 'Nếu lỗi vẫn tiếp tục, hãy kiểm tra kết nối mạng',
    'per_month': '/tháng',
    'no_meme_to_share': 'Không có meme để chia sẻ!',

    // Transaction form options
    'select_type': '-- Chọn loại --',
    'select_category': '-- Chọn danh mục --',
    'expense_category': 'Danh mục chi tiêu',
    
    // Expense categories
    'food': '🍜 Ăn uống',
    'coffee': '☕ Cafe',
    'transport': '🚗 Di chuyển',
    'shopping': '🛒 Mua sắm',
    'entertainment': '🎬 Giải trí',
    'health': '🏥 Sức khỏe',
    'education': '📚 Giáo dục',
    'utilities': '⚡ Tiện ích',
    'other': '📦 Khác',

    // Future Me Scenarios
    'scenario_reduce_coffee': 'Nếu bớt coffee 1 ly/ngày',
    'scenario_reduce_coffee_desc': 'Giảm 1 ly coffee mỗi ngày (30k/ly)',
    'scenario_cook_at_home': 'Nếu ăn nhà thêm 2 bữa/tuần',
    'scenario_cook_at_home_desc': 'Giảm 30% chi phí ăn uống bằng cách nấu ăn tại nhà',
    'scenario_increase_investment': 'Nếu đầu tư thêm 500k/tháng',
    'scenario_increase_investment_desc': 'Tăng đầu tư thêm 500,000₫ mỗi tháng',
    'scenario_reduce_transport': 'Nếu đi xe máy/đi bộ nhiều hơn',
    'scenario_reduce_transport_desc': 'Giảm 25% chi phí đi lại',

    // Future Me Goals
    'goal_iphone_16_pro_max': 'iPhone 16 Pro Max',
    'goal_honda_wave': 'Honda Wave RSX',
    'goal_dalat_trip': 'Du lịch Đà Lạt',
    'goal_emergency_fund': 'Quỹ khẩn cấp (6 tháng)',
    'goal_laptop_macbook': 'MacBook Air M3',
    'goal_motorbike_upgrade': 'Upgrade xe máy',
    'goal_time_under_1_month': 'Dưới 1 tháng',
    'goal_time_months_only': '{months} tháng',
    'goal_time_years_only': '{years} năm', 
    'goal_time_years_months': '{years} năm {months} tháng',
    'goal_time_not_achievable': 'Không thể đạt được với mô hình chi tiêu hiện tại'
};

// Export for use in i18n.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = viTranslations;
} else {
    window.viTranslations = viTranslations;
} 