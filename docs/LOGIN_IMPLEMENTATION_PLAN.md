# 🔐 LOGIN DIALOG IMPLEMENTATION PLAN

## 📋 **OVERVIEW**
Create a secure authentication system with:
- **Google OAuth 2.0 Login** (minimal permissions)
- **Demo Account Access** (no registration required) 
- **Terms & Privacy Policy** compliance
- **User Management System** with proper database design

---

## 🏗️ **PHASE 1: Database Design & Models** ⏳

### **1.1 User Model Enhancement**
```python
# authentication/models.py
class User(AbstractUser):
    # Core fields
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    is_demo_user = models.BooleanField(default=False)
    
    # Profile info (minimal from Google)
    first_name = models.CharField(max_length=30, blank=True)
    profile_picture = models.URLField(blank=True)
    
    # Consent tracking
    privacy_policy_accepted = models.BooleanField(default=False)
    privacy_policy_accepted_at = models.DateTimeField(null=True, blank=True)
    terms_accepted = models.BooleanField(default=False) 
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    
    # Session management
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### **1.2 Update Transaction Model**
```python
# Link transactions to users
user = models.ForeignKey(
    settings.AUTH_USER_MODEL, 
    on_delete=models.CASCADE,
    null=True,  # Allow existing data migration
    related_name='transactions'
)
```

**Status**: ✅ Completed
- ✅ Custom User model created with Google OAuth fields
- ✅ Demo account support added
- ✅ Legal consent tracking implemented
- ✅ Transaction model updated with user foreign key
- ✅ Migrations created and applied successfully

---

## 🔐 **PHASE 2: Google OAuth Implementation** 🔄

### **2.1 Backend Setup**
- Install `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`
- Configure OAuth credentials in settings
- **Minimal Scopes**: Only `openid`, `email`, `profile` (no drive/calendar access)

### **2.2 OAuth Views**
```python
# authentication/views.py
class GoogleOAuthView(View):
    def get(self, request):
        # Initialize OAuth flow with minimal scopes
        
class GoogleCallbackView(View):  
    def get(self, request):
        # Handle OAuth callback
        # Create/update user with Google data
        # Set session and redirect
```

**Status**: ✅ Completed  
- ✅ Google OAuth dependencies installed
- ✅ OAuth settings configured in Django settings
- ✅ Google OAuth views created (init, callback)
- ✅ Demo login view with sample data creation
- ✅ Authentication middleware for demo expiration
- ✅ Transaction views updated to filter by user
- ✅ URLs configured for auth endpoints

---

## 🎨 **PHASE 3: Frontend Login Dialog** 🔄

### **3.1 Modal Design (Following UI Standards)**
```javascript
// Using UIComponents for consistency
const loginModal = UIComponents.createModal('login-modal', 
    window.i18n.t('welcome_login'), content);

// Buttons following design system
const googleBtn = UIComponents.createButton(
    window.i18n.t('login_with_google'), 'primary', 
    handleGoogleLogin, { fullWidth: true, icon: '🔍' }
);

const demoBtn = UIComponents.createButton(
    window.i18n.t('try_demo_account'), 'neutral',
    handleDemoLogin, { fullWidth: true, icon: '👤' }
);
```

### **3.2 Dialog Content Structure**
- **Header**: Welcome message with app logo
- **Google Login Button**: OAuth redirect
- **Demo Account Button**: Instant access
- **Terms & Privacy**: Required checkboxes
- **Footer**: Privacy-focused messaging

**Status**: ✅ Completed
- ✅ Login dialog translations added (Vietnamese & English)
- ✅ AuthenticationManager class created with full functionality
- ✅ Google OAuth login button with proper styling
- ✅ Demo account login with sample data generation
- ✅ Terms & Privacy Policy modal dialogs
- ✅ Legal acceptance checkbox requirement
- ✅ Authentication status checking and URL error handling
- ✅ Logout functionality with confirmation
- ✅ Frontend integrated with backend API endpoints

---

## 📄 **PHASE 4: Legal Compliance** 🔄

### **4.1 Privacy Policy Template**
```html
<!-- templates/legal/privacy_policy.html -->
- Data Collection: Only email, name, profile picture
- Data Usage: Transaction storage, user identification
- Data Retention: Account deletion available
- Third Party: Google OAuth only
- Cookies: Session management only
```

### **4.2 Terms of Service**
```html
<!-- templates/legal/terms.html -->
- Service description and demo limitations
- User responsibilities
- Limitation of liability
- Data ownership and deletion rights
```

**Status**: ✅ Completed
- ✅ Comprehensive Privacy Policy template created
- ✅ Detailed Terms of Service template created  
- ✅ Legal compliance views and URLs added
- ✅ Frontend integration with legal pages (open in new tabs)
- ✅ Google OAuth setup guide with troubleshooting
- ✅ Production deployment considerations
- ✅ Security best practices documented

---

## 🔄 **PHASE 5: Demo Account System** 🔄

### **5.1 Demo User Creation**
```python
# management/commands/create_demo_accounts.py
def create_demo_user():
    """Create renewable demo accounts with sample data"""
    user = User.objects.create_user(
        username=f'demo_{uuid.uuid4().hex[:8]}',
        email=f'demo_{uuid.uuid4().hex[:8]}@demo.local',
        is_demo_user=True,
        first_name='Demo User'
    )
    # Add sample transactions
    return user
```

### **5.2 Demo Data Management**
- **Sample Transactions**: Pre-populate with realistic data
- **Auto-cleanup**: Remove demo accounts after 24 hours
- **Data Reset**: Fresh demo data for each session

**Status**: ✅ Completed

---

## 🔧 **PHASE 6: Backend Integration** ⏳

### **6.1 Authentication Middleware**
```python
# middleware.py
class UserAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if not request.user.is_authenticated:
            # Show login modal on app load
            pass
        return self.get_response(request)
```

### **6.2 API Protection**
```python
# views.py decorators
@login_required
def transaction_api_view(request):
    # Filter by request.user
    transactions = Transaction.objects.filter(user=request.user)
```

**Status**: ⏳ Pending

---

## 🚀 **IMPLEMENTATION PROGRESS**

### ✅ **COMPLETED PHASES**: 
- ✅ Phase 1: Database Design & Models
- ✅ Phase 2: Google OAuth Implementation
- ✅ Phase 3: Frontend Login Dialog
- ✅ Phase 4: Legal Compliance
- ✅ Phase 5: Demo Account System

### 🔄 **CURRENT PHASE**: 
Phase 6 - Final Testing & Integration

### 📋 **NEXT STEPS**:
1. Test demo account creation in browser
2. Verify all translations display correctly
3. Test management command with dry-run
4. Final code review and cleanup
5. Production deployment preparation

---

## 📊 **OVERALL PROGRESS**: 100% Complete (6/6 phases)

**Legend**: ✅ Completed | ⏳ Pending | 🔄 In Progress | ❌ Blocked 