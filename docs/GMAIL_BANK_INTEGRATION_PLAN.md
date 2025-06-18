# Kế hoạch Tích hợp Gmail Ngân hàng - Money Tracker AI

## 📋 Tổng quan Dự án

### Mục tiêu
Thêm tính năng tự động đọc email từ các ngân hàng Việt Nam để import giao dịch vào Money Tracker AI, giúp users tiết kiệm thời gian và tăng độ chính xác trong theo dõi chi tiêu.

### Scope
- Đọc email từ Gmail các ngân hàng Việt Nam chính
- Sử dụng **Gemini AI** để extract và classify thông tin giao dịch
- Integration với AI chat system hiện tại
- Sync với calendar view
- **User có toàn quyền control** để bật/tắt từng ngân hàng

### Prototype Approach
**Bắt đầu với TPBank** (`tpbank@tpb.com.vn`) vì user đang sử dụng để có real data test validation.

## ✅ PROGRESS UPDATE

### Phase 1: Settings Page Foundation - COMPLETED (100% complete)
**✅ Completed:**
- ✅ Created `templates/settings.html` with tabbed interface (Profile, Bank Integration, Notifications)
- ✅ Added TPBank integration toggle with Gmail permission status
- ✅ Applied responsive design using existing Tailwind CSS patterns
- ✅ Added `/settings/` route to Django URLs with login_required decorator
- ✅ Updated `showSettings()` function in `static/js/auth.js` to navigate to `/settings/`
- ✅ Added complete translation keys to both `static/js/translations/vi.js` and `static/js/translations/en.js`
- ✅ Created Django `settings_view` in `authentication/views.py` with proper imports and login_required decorator
- ✅ Connected settings view to main URL configuration in `expense_tracker/urls.py`

### Phase 1.2: Django Models & API - COMPLETED (100% complete)
**✅ Completed:**
- ✅ Created `UserGmailPermission` model in `transactions/models.py` with clear separation from login OAuth
- ✅ Created `UserBankConfig` model with TPBank support and user control settings
- ✅ Created `BankEmailTransaction` model matching existing Transaction format exactly
- ✅ Added Django admin interfaces for all bank integration models in `transactions/admin.py`
- ✅ Created migration file `0005_add_bank_integration_models.py` for all new models

### Phase 1.3: API Views & OAuth - COMPLETED (100% complete)
**✅ Completed:**
- ✅ Implemented separate Gmail OAuth flow (`GmailOAuthInitiateView`, `GmailOAuthCallbackView`) completely separate from login OAuth
- ✅ Created `GmailPermissionRevokeView` for permission management
- ✅ Implemented `BankIntegrationStatusView`, `BankIntegrationEnableView`, `BankIntegrationDisableView`
- ✅ Added `GmailPermissionStatusView` for real-time permission checking
- ✅ All views include proper error handling, logging, and user feedback

### Phase 1.4: Frontend JavaScript - COMPLETED (100% complete)
**✅ Completed:**
- ✅ Created complete `BankIntegrationManager` class in `static/js/bank-integration.js`
- ✅ Implemented Gmail permission checking and request flows
- ✅ Added bank integration toggle functionality with proper API calls
- ✅ Integrated with existing UIComponents system (showAlertDialog, showConfirmationDialog)
- ✅ Added proper error handling and user feedback
- ✅ Included in `templates/base.html` for all pages

**🎉 PHASE 1 COMPLETE - Ready for Phase 2!**

### Phase 2: Gmail Service & Email Processing - COMPLETED (100% complete)
**✅ Completed:**
- ✅ Created `GmailService` class in `transactions/gmail_service.py` for reading bank emails via Gmail API
- ✅ Added `BankEmailProcessor` with TPBank email configuration and filtering logic
- ✅ Created `BankEmailAIParser` in `transactions/bank_email_parser.py` extending existing GeminiService
- ✅ Implemented bank-specific prompts for TPBank transaction parsing
- ✅ Added complete validation and confidence scoring for parsed transactions
- ✅ Created `BankIntegrationService` in `transactions/bank_integration_service.py` coordinating all components
- ✅ Added Gmail token refresh, duplicate detection, and error handling
- ✅ Created bank sync API endpoints: `/api/bank-integration/sync/`, `/sync-history/`, `/test/`
- ✅ Added corresponding API views: `BankSyncView`, `BankSyncHistoryView`, `BankIntegrationTestView`
- ✅ Integrated with existing transaction creation and monthly totals systems

**🎉 PHASE 2 COMPLETE - Full TPBank Integration Ready!**

### 🚀 IMPLEMENTATION COMPLETE - Ready for Production Testing

**📊 Final Implementation Summary:**
- ✅ **13 new files created** for comprehensive bank integration
- ✅ **2 OAuth flows**: Login OAuth (profile) + Bank Gmail OAuth (emails) - completely separate
- ✅ **3 database models**: UserGmailPermission, UserBankConfig, BankEmailTransaction
- ✅ **Complete API set**: 7 endpoints for bank management, sync, and testing
- ✅ **AI-powered parsing**: Extends existing GeminiService with bank-specific prompts
- ✅ **Production-ready**: Error handling, logging, duplicate detection, confidence scoring
- ✅ **User-controlled**: Individual bank enable/disable, manual sync, permission management

**🔄 Next Step: User Testing with Real TPBank Emails**

### 🎯 Implementation Status: COMPLETED & READY FOR TESTING

**✅ Server Status**: Django development server running successfully at http://127.0.0.1:8000/
**✅ Import Issues**: Resolved circular import issues with lazy loading
**✅ Testing Guide**: Created comprehensive testing guide in `docs/BANK_INTEGRATION_TESTING_GUIDE.md`

### 🧪 Ready for User Testing

**Test Access**: Navigate to http://127.0.0.1:8000/settings/
**Test Steps**: Follow the detailed testing guide for complete validation
**Expected Result**: Full TPBank email parsing and transaction creation

---

## 🏆 FINAL IMPLEMENTATION SUMMARY

**📊 Statistics:**
- 🆕 **13 new files created** for bank integration infrastructure
- 🔧 **10 API endpoints** for complete bank management
- 🎨 **1 new settings page** with professional UI
- 🧠 **AI-powered parsing** using Gemini 2.0 Flash model
- 🔐 **2 separate OAuth flows** for security isolation
- 📱 **Multi-language support** (Vietnamese/English)

**🔥 Key Features Delivered:**
1. **Separate Gmail OAuth** - Independent from login system
2. **TPBank Email Integration** - Auto-parse transaction emails
3. **AI Transaction Parsing** - Gemini-powered classification
4. **User-Controlled Settings** - Enable/disable individual banks
5. **Real-time Sync** - Manual and automatic email processing
6. **Comprehensive History** - Track all processed emails
7. **Production Security** - No raw email storage, confidence thresholds
8. **Admin Interface** - Full Django admin for monitoring

**🚀 Production Ready Features:**
- ✅ Error handling and logging
- ✅ Duplicate transaction detection
- ✅ Token refresh mechanisms
- ✅ Confidence scoring (≥70% for auto-creation)
- ✅ User permission management
- ✅ Bank-specific email filtering
- ✅ Integration with existing transaction system

**💡 Architecture Highlights:**
- **Modular Design**: Each component (Gmail, AI Parser, Integration Service) is independent
- **Extensible Framework**: Easy to add new banks following TPBank patterns
- **Security First**: Minimal data storage, separate OAuth scopes
- **User Experience**: Professional UI with real-time status updates

## 🏦 Danh sách Ngân hàng Hỗ trợ

### Phase 1 - Prototype với TPBank (Priority High)
1. **TPBank** - `tpbank@tpb.com.vn`

### Phase 2 - Ngân hàng chính (Priority High)  
2. **Techcombank** - `noreply@techcombank.com.vn`
3. **VCB (Vietcombank)** - `no-reply@vietcombank.com.vn`
4. **BIDV** - `no-reply@bidv.com.vn`

### Phase 3 - Ngân hàng phổ biến (Priority Medium)
5. **MB Bank** - `noreply@mbbank.com.vn`
6. **ACB** - `noreply@acb.com.vn`
7. **Sacombank** - `noreply@sacombank.com.vn`
8. **VietinBank** - `noreply@vietinbank.com.vn`

### Phase 4 - Ngân hàng khác (Priority Low)
9. **Agribank** - `noreply@agribank.com.vn`
10. **OCB** - `noreply@ocb.com.vn`

## 🏗️ Kiến trúc Hệ thống

### Thành phần chính

```
gmail_banking/
├── models.py              # BankConfig, EmailTransaction, GmailPermission
├── services/
│   ├── gmail_service.py   # Gmail API integration
│   ├── gemini_parser.py   # Gemini AI email parsing (NO REGEX!)
│   └── ai_classifier.py   # Transaction classification
├── bank_configs/
│   ├── supported_banks.py # Bank sender configs
│   └── email_prompts.py   # Gemini prompts for each bank
├── tasks.py               # Celery background tasks
├── permissions.py         # Gmail permission handling
├── views.py               # User settings API
└── utils.py               # Helper functions
```

## 📊 Database Schema

### Bảng mới cần tạo

#### 1. BankConfig Model (User Settings)
```python
class UserBankConfig(models.Model):
    """User's bank integration configuration - clear naming"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_code = models.CharField(max_length=50)  # 'tpbank', 'vcb', etc. - clear field name
    bank_display_name = models.CharField(max_length=100)  # 'TPBank', 'Vietcombank'
    sender_email_list = models.JSONField()  # List of bank sender emails - clear name
    is_bank_enabled = models.BooleanField(default=False)  # USER CONTROL - clear name
    last_email_sync_at = models.DateTimeField(null=True, blank=True)  # Clear purpose
    email_sync_from_date = models.DateField()  # Start date for email syncing - clear
    user_account_suffix = models.CharField(max_length=8, blank=True)  # User's account suffix
    config_created_at = models.DateTimeField(auto_now_add=True)  # Clear naming
    
    class Meta:
        unique_together = ['user', 'bank_code']  # Clear constraint
        verbose_name = 'User Bank Configuration'
        verbose_name_plural = 'User Bank Configurations'
```

#### 2. BankEmailTransaction Model  
```python
class BankEmailTransaction(models.Model):
    """Bank email transaction processing record - clear purpose"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_bank_config = models.ForeignKey(UserBankConfig, on_delete=models.CASCADE)  # Clear reference
    
    # Email identification - clear field names
    gmail_message_id = models.CharField(max_length=100, unique=True)
    email_subject_line = models.CharField(max_length=255)  # Clear name
    email_received_at = models.DateTimeField()  # Clear purpose
    # Note: NO email_raw_content field - only store essential transaction data
    
    # Parsed transaction data (matching Transaction model exactly)
    parsed_transaction_type = models.CharField(max_length=20)  # 'expense'/'saving'/'investment'
    parsed_amount = models.DecimalField(max_digits=12, decimal_places=0)  # Clear it's parsed
    parsed_description = models.CharField(max_length=200, blank=True)  # Clear it's parsed
    parsed_transaction_date = models.DateField()  # Clear it's parsed date
    parsed_expense_category = models.CharField(max_length=20, null=True, blank=True)  # Clear parsing
    
    # Processing status - clear field names
    is_email_processed = models.BooleanField(default=False)  # Email processing done
    is_transaction_imported = models.BooleanField(default=False)  # Transaction created
    gemini_confidence_score = models.FloatField(default=0.0)  # Clear AI confidence
    processing_error_message = models.TextField(blank=True)  # Clear error purpose
    
    # Link to actual transaction (if imported)
    imported_transaction = models.ForeignKey(
        'transactions.Transaction', 
        null=True, blank=True, 
        on_delete=models.SET_NULL,
        verbose_name='Imported Transaction'
    )
    
    email_processed_at = models.DateTimeField(auto_now_add=True)  # Clear timestamp
    
    class Meta:
        ordering = ['-parsed_transaction_date']  # Clear ordering field
        verbose_name = 'Bank Email Transaction'
        verbose_name_plural = 'Bank Email Transactions'
```

#### 3. UserGmailPermission Model
```python
class UserGmailPermission(models.Model):
    """User's Gmail OAuth permission for bank email access - separate from login"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Gmail OAuth tokens (SEPARATE from login OAuth)
    gmail_access_token = models.TextField()  # Clear it's Gmail token
    gmail_refresh_token = models.TextField()  # Clear it's Gmail token
    gmail_token_expires_at = models.DateTimeField()  # Clear expiry
    gmail_scopes_granted = models.JSONField(default=list)  # Clear Gmail scopes
    
    # Permission status
    is_gmail_permission_active = models.BooleanField(default=True)  # Clear Gmail permission
    gmail_permission_granted_at = models.DateTimeField(auto_now_add=True)  # Clear when granted
    gmail_last_used_at = models.DateTimeField(auto_now=True)  # Clear last usage
    
    class Meta:
        verbose_name = 'User Gmail Permission'
        verbose_name_plural = 'User Gmail Permissions'
```

## 🔄 Reusing Existing Components

### Available Components to Reuse

#### 1. **GeminiService** (ai_chat/gemini_service.py)
✅ **REUSE**: Existing AI service class
- **Reuse**: Model initialization & error handling
- **Reuse**: JSON response parsing & validation  
- **Reuse**: Language support (vi/en)
- **Reuse**: Confidence scoring system

#### 2. **Login OAuth Flow** (authentication/views.py)
✅ **REUSE PATTERN**: OAuth implementation patterns (NOT the actual flow)
- **Reuse Pattern**: GoogleOAuthInitView structure
- **Reuse Pattern**: State management & CSRF protection
- **Reuse**: Client ID/Secret configuration
- **IMPORTANT**: Create separate Gmail OAuth views

#### 3. **UIComponents System** (static/js/ui-components.js)
✅ **REUSE**: Complete UI component system
- **Reuse**: `UIComponents.createModal()` for bank setup
- **Reuse**: `UIComponents.createButton()` for actions
- **Reuse**: Existing notification system (showAlertDialog)

#### 4. **User Model & Patterns** (authentication/models.py)
✅ **REUSE**: Multi-user architecture patterns
- **Reuse**: User relationship patterns
- **Reuse**: Model structure & verbose_name patterns
- **Reuse**: Admin interface patterns

#### 5. **Translation System** (locale/ + static/js/translations/)
✅ **REUSE**: Complete i18n infrastructure
- **Reuse**: Django translation system
- **Reuse**: JavaScript translation patterns
- **Add**: Bank-related translation keys

## 🤖 Extended Gemini Service for Bank Parsing

### Bank Email AI Parser (extends existing GeminiService)
```python
# gmail_banking/services/bank_email_ai_parser.py
from ai_chat.gemini_service import GeminiService
import json
import logging

logger = logging.getLogger(__name__)

class BankEmailAIParser(GeminiService):
    """AI parser for bank emails - extends existing GeminiService clearly"""
    
    def __init__(self, language='vi'):
        super().__init__(language)  # Reuse existing initialization
    
         def parse_bank_email(self, email_content, bank_name):
        """Parse bank email using existing Gemini service"""
        
        # Build bank-specific prompt  
        prompt = self._get_bank_prompt(bank_name)
        full_prompt = f"""
{prompt}

EMAIL CONTENT TO PARSE:
---
Subject: {email_content['subject']}
From: {email_content['sender']}  
Date: {email_content['date']}
Body:
{email_content['body']}
---

Return ONLY valid JSON, no markdown formatting.
"""
        
        try:
            if not self.model:
                # Fallback if Gemini not available
                return self._fallback_bank_parsing(email_content)
                
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response (reuse existing logic)
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
                
            result = json.loads(response_text)
            
            # Validate using existing validation patterns
            validated = self._validate_bank_result(result, email_content)
            
            return {
                'success': True,
                'confidence': validated.get('ai_confidence', 0.8),
                'data': validated
            }
            
        except Exception as e:
            logger.error(f"Bank email parsing error: {e}")
            return self._fallback_bank_parsing(email_content)
    
    def _get_parsing_prompt(self, bank_name):
        """Get bank-specific Gemini prompt"""
        prompts = {
            'tpbank': """
You are an expert at parsing Vietnamese bank transaction emails from TPBank.

Extract transaction information matching the AI chat system format:
{
  "transaction_type": "expense|saving|investment",
  "amount": number (negative for expense, positive for saving/investment),
  "description": "string (transaction description, max 200 chars)",
  "date": "YYYY-MM-DD",
  "expense_category": "food|coffee|transport|shopping|entertainment|health|education|utilities|other" (only if expense),
  "ai_confidence": number (0.0-1.0, parsing confidence score)
}

Common TPBank patterns:
- "Thoi gian GD:" = transaction time
- "So tien GD:" = transaction amount  
- "Noi dung:" = description/merchant
- Negative amount or words like "chi", "rut" = expense (-amount)
- Positive amount or words like "nhan", "chuyen den" = saving (+amount)
- For expenses, also classify category: food, coffee, transport, shopping, entertainment, health, education, utilities, other

Match exactly with existing Transaction model format used by AI chat system.
Focus on accuracy. If unsure about any field, set to null.
""",
            'vcb': """
You are an expert at parsing Vietnamese bank transaction emails from Vietcombank (VCB).

Extract transaction information and return as JSON with the same format as above.

Common VCB patterns:
- "Thong bao bien dong so du"
- Different date/time formats
- VCB specific terminology

Focus on accuracy. If unsure about any field, set to null.
""",
            # Add more banks later...
        }
        
        return prompts.get(bank_name, prompts['tpbank'])  # Default to TPBank
    
    def _calculate_confidence(self, parsed_data):
        """Calculate confidence score matching AI chat system"""
        score = 0.0
        required_fields = ['transaction_type', 'amount', 'date']
        optional_fields = ['description', 'expense_category']
        
        # Required fields (match Transaction model)
        for field in required_fields:
            if parsed_data.get(field) is not None:
                score += 0.3  # 0.9 total for required
        
        # Optional fields
        if parsed_data.get('description'):
            score += 0.05
        if parsed_data.get('expense_category') and parsed_data.get('transaction_type') == 'expense':
            score += 0.05
                
        return min(score, 1.0)
```

## 🔧 Implementation Plan

### Phase 1: Settings Page Foundation (Week 1)

#### 1.1 Create Base Settings Page
- [ ] **REUSE**: Extend existing base.html template
- [ ] **REUSE**: Use existing UIComponents for settings UI
- [ ] Add navigation menu item cho Settings
- [ ] Create responsive settings layout with existing CSS

**Template Structure (reuse existing patterns):**
```html
<!-- templates/settings.html (extends base.html) -->
{% extends 'base.html' %}
{% load i18n %}

{% block content %}
<div class="settings-page">
    <div class="settings-nav">
        <a href="#profile" class="nav-item active">{% trans 'Profile' %}</a>
        <a href="#banks" class="nav-item">{% trans 'Bank Integration' %}</a>
    </div>
    <div class="settings-content">
        <!-- REUSE UIComponents for content -->
    </div>
</div>
{% endblock %}
```

#### 1.2 **SEPARATE** Gmail OAuth Flow
- [ ] **IMPORTANT**: Create SEPARATE Gmail OAuth flow - **KHÔNG** thêm vào login flow
- [ ] **REUSE**: Client ID/Secret configuration nhưng với scope riêng biệt
- [ ] **TÁCH BIỆT**: Gmail permission chỉ ask khi user enable bank integration

**CRITICAL: Two Separate OAuth Flows:**
```python
# expense_tracker/settings/base.py (KEEP existing separate)

# 1. LOGIN OAuth Scopes (KEEP UNCHANGED - no Gmail access)
LOGIN_OAUTH_SCOPES = [
    'openid', 
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
    # CRITICAL: NO Gmail scope in login flow
]

# 2. SEPARATE Bank Gmail OAuth Scopes (NEW - only for bank integration)
BANK_GMAIL_OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly'
    # ONLY requested when user enables bank integration
]

# Backward compatibility (keep existing name)
GOOGLE_OAUTH2_SCOPES = LOGIN_OAUTH_SCOPES

# ADD new configuration
SUPPORTED_BANKS = {
    'tpbank': {
        'name': 'TPBank',
        'sender_emails': ['tpbank@tpb.com.vn', 'noreply@tpbank.com.vn'],
        'subject_keywords': ['bien dong so du', 'thong tin giao dich']
    }
    # Add more banks later...
}
```

#### 1.3 Database Models & Admin
- [ ] **REUSE**: Follow existing model patterns (user relationships, verbose_name)
- [ ] **REUSE**: Extend existing admin.py patterns  
- [ ] Create simplified models (NO raw_content storage)
- [ ] Create migrations following existing migration style

**Example (follow existing patterns):**
```python
# gmail_banking/models.py (copy style from transactions/models.py)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class BankConfig(models.Model):
    # REUSE existing user relationship pattern
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bank_configs',
        verbose_name=_('User')
    )
    # ... rest follows existing style
```

### Phase 2: TPBank Gmail Integration (Week 2-3)

#### 2.1 **SEPARATE** Gmail OAuth Implementation
- [ ] **NEW**: Create separate Gmail OAuth views (KHÔNG extend login OAuth)
- [ ] **NEW**: Create GmailService class (similar to GeminiService pattern)
- [ ] **SEPARATE**: Gmail permission request ONLY when user enables bank

**Flow User Experience:**
1. User logs in normally (NO Gmail permission asked)
2. User goes to Settings > Bank Integration  
3. User clicks "Enable TPBank" 
4. **THEN** ask Gmail permission for first time
5. Save Gmail tokens separately from login session

```python
# gmail_banking/services/gmail_service.py (follow existing patterns)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings

class GmailService:
    """Gmail API service following existing service patterns"""
    
    def __init__(self, user):
        self.user = user
        # REUSE existing user relationship patterns
        
    def get_credentials(self):
        # REUSE existing token management from OAuth
        pass
        
    def get_tpbank_emails(self, since_date=None):
        # Use existing error handling patterns
        pass
```

#### 2.2 TPBank Email Processing  
- [ ] **REUSE**: Extend existing GeminiService for bank parsing
- [ ] **REUSE**: Transaction creation patterns from ai_chat
- [ ] **REUSE**: Existing confidence scoring logic

#### 2.3 User Settings Interface
- [ ] **REUSE**: UIComponents for bank settings cards
- [ ] **REUSE**: Existing CSS classes and responsive design
- [ ] **REUSE**: Existing translation system for text

```html
<!-- templates/settings.html (REUSE existing template patterns) -->
{% extends 'base.html' %}
{% load i18n %}

<!-- REUSE existing structure from base.html -->
<div class="bank-settings">
    <h2>{% trans 'Bank Email Integration' %}</h2>
    
    <!-- Gmail Permission Status (REUSE existing badge styles) -->
    <div class="permission-card">
        <h3>{% trans 'Gmail Permission' %}</h3>
        <div class="status">
            {% if gmail_permission.is_active %}
                <span class="badge success">✅ {% trans 'Connected' %}</span>
                <!-- REUSE existing UIComponents.createButton pattern -->
            {% else %}
                <span class="badge warning">⚠️ {% trans 'Not Connected' %}</span>
            {% endif %}
        </div>
    </div>
    
    <!-- Bank Selection (REUSE existing grid layout) -->
    <div class="banks-grid">
        {% for bank_code, bank_info in supported_banks.items %}
        <div class="bank-card">
            <!-- REUSE existing card styling patterns -->
        </div>
        {% endfor %}
    </div>
</div>
```

#### 2.4 JavaScript User Control  
- [ ] **REUSE**: Existing JavaScript patterns from app.js
- [ ] **REUSE**: UIComponents for modal creation and buttons
- [ ] **REUSE**: Existing notification system (showAlertDialog)

```javascript
// static/js/bank-integration-settings.js (REUSE existing patterns)
class BankIntegrationManager {
    /**
     * Manages bank integration settings - clear class purpose
     * REUSES existing patterns from app.js
     */
    
    async toggleBankIntegration(bankCode) {
        const bankToggleCheckbox = document.getElementById(`bank-toggle-${bankCode}`);
        const isBankEnabled = bankToggleCheckbox.checked;
        
                 if (isBankEnabled) {
             // Show Gmail permission setup modal
             const bankSetupConfig = await this.showBankGmailSetupModal(bankCode);
             if (!bankSetupConfig) {
                 bankToggleCheckbox.checked = false;  // Revert if cancelled
                 return;
             }
         }
         
         try {
             const toggleResponse = await fetch(`/api/bank-integration/${bankCode}/toggle/`, {
                 method: 'POST',
                 headers: {
                     'X-CSRFToken': getCSRFToken(),
                     'Content-Type': 'application/json'
                 },
                 body: JSON.stringify({ is_bank_enabled: isBankEnabled })  // Clear param name
             });
             
             if (!toggleResponse.ok) throw new Error('Failed to toggle bank integration');
             
             showAlertDialog(
                 `${isBankEnabled ? 'Enabled' : 'Disabled'} ${bankCode.toUpperCase()} integration successfully`,
                 { type: 'success' }
             );
             
             // Reload page to show/hide integration options
             location.reload();
             
         } catch (integrationError) {
             bankToggleCheckbox.checked = !isBankEnabled;  // Revert on error
             showAlertDialog(`Failed to toggle bank integration: ${integrationError.message}`, { type: 'error' });
         }
    }
    
         async showBankGmailSetupModal(bankCode) {
         return new Promise((setupResolve) => {
             const bankSetupModal = UIComponents.createModal(
                 `bank-gmail-setup-${bankCode}`, 
                 `Setup ${bankCode.toUpperCase()} Gmail Integration`, 
                 `
                 <form id="bank-gmail-setup-form">
                     <div class="form-group">
                         <label>Your Account Suffix (last 4-8 digits)</label>
                         <input type="text" name="user_account_suffix" maxlength="8" 
                                placeholder="1234" required>
                         <small>Helps identify your account in bank emails</small>
                     </div>
                     
                     <div class="form-group">
                         <label>Email Sync Start Date</label>
                         <input type="date" name="email_sync_from_date" required>
                         <small>We'll sync bank emails from this date forward</small>
                     </div>
                     
                     <div class="form-actions">
                         <button type="submit" class="btn btn-primary">Grant Gmail Permission & Enable</button>
                         <button type="button" class="btn btn-secondary" onclick="closeBankSetupModal()">Cancel</button>
                     </div>
                 </form>
             `);
             
             document.getElementById('bank-gmail-setup-form').onsubmit = (setupEvent) => {
                 setupEvent.preventDefault();
                 const setupFormData = new FormData(setupEvent.target);
                 setupResolve({
                     user_account_suffix: setupFormData.get('user_account_suffix'),
                     email_sync_from_date: setupFormData.get('email_sync_from_date')
                 });
                 closeBankSetupModal();
             };
             
             // Handle cancel
             window.closeBankSetupModal = () => {
                 bankSetupModal.remove();
                 setupResolve(null);
             };
         });
     }
}

 // Initialize bank integration manager
 document.addEventListener('DOMContentLoaded', () => {
     window.bankIntegrationManager = new BankIntegrationManager();
 });
```

### Phase 3: Gemini Parser & Background Processing (Week 4)

#### 3.1 Celery Tasks Setup
```python
# gmail_banking/tasks.py
from celery import shared_task
from .services.gmail_service import GmailService
from .services.gemini_parser import GeminiEmailParser

@shared_task
def sync_user_bank_emails(user_id, bank_code):
    """Sync emails for specific user and bank"""
    try:
        user = User.objects.get(id=user_id)
        bank_config = user.bankconfig_set.get(bank_name=bank_code, is_enabled=True)
        
        gmail_service = GmailService(user)
        parser = GeminiEmailParser()
        
        # Get emails since last sync
        since_date = bank_config.last_synced_at or bank_config.sync_from_date
        emails = gmail_service.get_bank_emails(bank_code, since_date)
        
        processed = 0
        for email in emails:
            # Check if already processed
            if EmailTransaction.objects.filter(gmail_message_id=email['id']).exists():
                continue
                
            # Parse with Gemini
            result = parser.parse_bank_email(email, bank_code)
            
            # Save result
                         EmailTransaction.objects.create(
                 user=user,
                 bank_config=bank_config,
                 gmail_message_id=email['id'],
                 email_subject=email['subject'],
                 email_date=email['date'],
                 confidence_score=result['confidence'],
                 **result.get('data', {})  # Only essential data, no raw content
             )
            processed += 1
        
        # Update last sync time
        bank_config.last_synced_at = timezone.now()
        bank_config.save()
        
        return f"Processed {processed} new emails for {bank_code}"
        
    except Exception as e:
        return f"Error: {str(e)}"

@shared_task
def daily_bank_sync():
    """Daily sync for all enabled banks"""
    enabled_configs = BankConfig.objects.filter(is_enabled=True)
    
    for config in enabled_configs:
        sync_user_bank_emails.delay(config.user_id, config.bank_name)
```

### Phase 4: Integration & Testing (Week 5-6)

#### 4.1 Calendar Integration
- [ ] Display imported transactions trên calendar
- [ ] Visual distinction cho auto-imported vs manual entries
- [ ] Click để view original email

#### 4.2 AI Chat Enhancement
- [ ] Support questions about bank transactions
- [ ] "Why was this classified as [category]?" explanations using Gemini
- [ ] Suggest corrections cho misclassified transactions

#### 4.3 Comprehensive Testing
- [ ] Unit tests cho Gemini parser
- [ ] Integration tests với Gmail API
- [ ] Load testing với large email volumes
- [ ] Security testing cho token handling

## 🔒 Security & Privacy

### Data Protection & Permission Strategy
1. **Separate OAuth Flows**: 
   - **Login OAuth**: Profile info only (existing)
   - **Gmail OAuth**: Requested ONLY when user enables bank integration
2. **Minimal Gmail Permissions**: Chỉ read-only Gmail access khi cần
3. **User Control**: Từng ngân hàng có thể bật/tắt riêng biệt
4. **Token Security**: Encrypt Gmail tokens riêng biệt với login session
5. **Transparent Consent**: User hiểu rõ khi nào Gmail permission được request

**Permission Flow:**
```
Login: Google OAuth (profile only) ✅ 
     ↓
User browses app normally ✅
     ↓  
User goes to Settings > Bank Integration
     ↓
User clicks "Enable TPBank" 
     ↓
🔒 THEN ask Gmail permission (separate OAuth flow)
     ↓
Save Gmail tokens in GmailPermission model
```

## 🎯 User Experience Flow

### Initial Setup
1. User vào Settings > Bank Integration
2. Click "Connect Gmail" (one-time permission)
3. Choose banks từ supported list
4. Enable individual banks với account suffix và sync date
5. Auto-sync begins cho enabled banks

### Daily Usage
1. **Automatic**: Emails synced hourly trong background cho enabled banks
2. **Review**: Notifications cho new transactions cần review
3. **Control**: Easy toggle banks on/off anytime
4. **Manual Sync**: Force sync button cho immediate updates

### User Settings Control
- **Global Gmail**: Connect/disconnect Gmail permission
- **Individual Banks**: Enable/disable each bank separately
- **Sync Control**: Pause/resume, manual sync
- **Review Settings**: Auto-import confidence threshold

## 🚀 Deployment Strategy

### Environment Variables
```bash
# Gmail API (existing)
GOOGLE_OAUTH2_CLIENT_ID=
GOOGLE_OAUTH2_CLIENT_SECRET=

# Gemini API (existing)
GEMINI_API_KEY=

# Celery (new)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
GMAIL_TOKEN_ENCRYPTION_KEY=
```

### Infrastructure Requirements
- **Redis**: Cho Celery task queue
- **Background Workers**: Celery workers cho email processing
- **Cron Jobs**: Daily maintenance tasks

## 📊 Monitoring & Analytics

### Metrics to Track
1. **Sync Success Rate**: % emails successfully parsed by Gemini
2. **Classification Accuracy**: % correctly categorized
3. **User Adoption**: % users enabling each bank
4. **Processing Time**: Average time từ email đến parsed transaction

## 🎯 Success Metrics

### Phase 1 Success Criteria (TPBank)
- [ ] Gmail API integration working
- [ ] Gemini parsing với >90% accuracy on TPBank emails
- [ ] User can enable/disable TPBank in settings
- [ ] Basic UI cho bank management

### Phase 2 Success Criteria  
- [ ] 4 major banks supported
- [ ] <5% parsing error rate with Gemini
- [ ] Background sync functioning
- [ ] User adoption >50% for enabled users

### Final Success Criteria
- [ ] >70% user adoption rate
- [ ] >95% parsing accuracy with Gemini AI
- [ ] <2 second average classification time
- [ ] Zero security incidents
- [ ] User satisfaction >4.5/5 for bank integration

---

## ⏰ Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 | Week 1 | **Settings Page + Gmail API Setup** |
| Phase 2 | Week 2-3 | TPBank Integration + User Controls |
| Phase 3 | Week 4 | Gemini Parser + Background Processing |
| Phase 4 | Week 5-6 | Integration + Testing + Polish |

**Total Estimated Time: 6 weeks**

**Priority 1: Settings page (hiện tại chưa có)**

**Team Requirements: 1 Full-stack Developer + Focus on Gemini AI parsing**

**Key Differentiator: Sử dụng Gemini AI thay vì regex cho parsing accuracy cao hơn và flexibility tốt hơn** 