from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Transaction(models.Model):
    """
    Simplified transaction model with 3 types: expense, saving, investment.
    Only expenses have categories, saving/investment are simple.
    """
    TRANSACTION_TYPES = [
        ('expense', _('🔴 Chi tiêu')),
        ('saving', _('🟢 Tiết kiệm')), 
        ('investment', _('🔵 Đầu tư'))
    ]
    
    # Simplified categories - only for expenses
    EXPENSE_CATEGORIES = [
        ('food', _('🍜 Ăn uống')),
        ('coffee', _('☕ Coffee')),
        ('transport', _('🚗 Di chuyển')),
        ('shopping', _('🛒 Mua sắm')),
        ('entertainment', _('🎬 Giải trí')),
        ('health', _('🏥 Sức khỏe')),
        ('education', _('📚 Giáo dục')),
        ('utilities', _('⚡ Tiện ích')),
        ('other', _('📦 Khác')),
    ]
    
    # Core fields
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPES,
        verbose_name=_('Transaction Type')
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        verbose_name=_('Amount')
    )
    description = models.CharField(
        max_length=200,
        verbose_name=_('Description')
    )
    date = models.DateField(
        verbose_name=_('Date')
    )
    
    # Only expense has categories, saving/investment are simple
    expense_category = models.CharField(
        max_length=20, 
        choices=EXPENSE_CATEGORIES, 
        null=True, 
        blank=True,
        verbose_name=_('Expense Category')
    )
    
    # User relationship - link transactions to users
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('User')
    )
    
    # AI related
    ai_confidence = models.FloatField(
        default=0.0,
        verbose_name=_('AI Confidence')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount:,}₫ - {self.date}"
    
    def get_icon(self):
        """Get icon based on transaction type and category"""
        if self.transaction_type == 'expense':
            category_icons = {
                'food': '🍜', 'coffee': '☕', 'transport': '🚗',
                'shopping': '🛒', 'entertainment': '🎬', 'health': '🏥',
                'education': '📚', 'utilities': '⚡', 'other': '📦'
            }
            return category_icons.get(self.expense_category, '📦')
        elif self.transaction_type == 'saving':
            return '💰'
        elif self.transaction_type == 'investment':
            return '📈'
        return '💰'
    
    def save(self, *args, **kwargs):
        """Override save to ensure category logic"""
        # Clear expense_category if not an expense
        if self.transaction_type != 'expense':
            self.expense_category = None
        
        # Ensure amount is positive for saving/investment, negative for expense
        if self.transaction_type == 'expense' and self.amount > 0:
            self.amount = -abs(self.amount)
        elif self.transaction_type in ['saving', 'investment'] and self.amount < 0:
            self.amount = abs(self.amount)
        
        super().save(*args, **kwargs)


class MonthlyTotal(models.Model):
    """Track monthly totals for dashboard"""
    # User relationship - CRITICAL FIX
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='monthly_totals',
        verbose_name=_('User')
    )
    
    year = models.IntegerField(verbose_name=_('Year'))
    month = models.IntegerField(verbose_name=_('Month'))
    
    total_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Total Amount')
    )
    expense_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Expense Amount')
    )
    saving_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Saving Amount')
    )
    investment_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name=_('Investment Amount')
    )
    transaction_count = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Updated')
    )
    
    class Meta:
        unique_together = ['user', 'year', 'month']  # CRITICAL: Updated constraint
        verbose_name = _('Monthly Total')
        verbose_name_plural = _('Monthly Totals')
        ordering = ['-year', '-month']
        indexes = [
            models.Index(fields=['user', 'year', 'month']),  # Performance index
            models.Index(fields=['user', '-year', '-month']),  # For ordering
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.year}/{self.month:02d} - Total: {self.total_amount:,.0f}₫" 


# =============================================================================
# BANK INTEGRATION MODELS (Phase 1 - Gmail Bank Integration)
# =============================================================================

class UserGmailPermission(models.Model):
    """
    Store Gmail OAuth tokens separate from login session
    
    CRITICAL: This is separate from User model's google_oauth_token
    - User.google_oauth_token = Login OAuth (profile info only)
    - UserGmailPermission.gmail_oauth_token = Bank Gmail OAuth (read emails)
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gmail_permission'
    )
    
    # Gmail OAuth tokens (separate from login OAuth)
    gmail_oauth_token = models.JSONField(null=True, blank=True, help_text="Gmail OAuth token for reading bank emails")
    gmail_token_expires_at = models.DateTimeField(null=True, blank=True)
    gmail_refresh_token = models.TextField(null=True, blank=True)
    
    # Permission status
    has_gmail_permission = models.BooleanField(default=False)
    permission_granted_at = models.DateTimeField(null=True, blank=True)
    permission_last_used = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Gmail Permission')
        verbose_name_plural = _('User Gmail Permissions')

    def __str__(self):
        status = "✅ Granted" if self.has_gmail_permission else "❌ Not Granted"
        return f"{self.user.get_short_name()} - Gmail Permission: {status}"

    def is_token_expired(self):
        """Check if Gmail token is expired"""
        if not self.gmail_token_expires_at:
            return True
        return timezone.now() > self.gmail_token_expires_at
    
    def refresh_token_if_needed(self):
        """Refresh Gmail token if expired and refresh token available"""
        if not self.is_token_expired():
            return True
            
        if not self.gmail_refresh_token:
            return False
            
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from django.conf import settings
            from django.utils import timezone
            
            # Recreate credentials from stored data
            creds = Credentials(
                token=self.gmail_oauth_token.get('token'),
                refresh_token=self.gmail_refresh_token,
                token_uri=self.gmail_oauth_token.get('token_uri'),
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                scopes=self.gmail_oauth_token.get('scopes', [])
            )
            
            # Refresh the token
            creds.refresh(Request())
            
            # Update stored tokens
            self.gmail_oauth_token = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes,
            }
            
            # Handle timezone for expiry
            if creds.expiry:
                if creds.expiry.tzinfo is None:
                    self.gmail_token_expires_at = timezone.make_aware(creds.expiry)
                else:
                    self.gmail_token_expires_at = creds.expiry
            else:
                self.gmail_token_expires_at = None
                
            self.gmail_refresh_token = creds.refresh_token
            self.permission_last_used = timezone.now()
            self.save()
            
            return True
            
        except Exception as e:
            # Refresh failed, permission needs to be re-granted
            print(f"Token refresh failed: {e}")
            return False

    def revoke_permission(self):
        """Revoke Gmail permission and clear tokens"""
        self.has_gmail_permission = False
        self.gmail_oauth_token = None
        self.gmail_token_expires_at = None
        self.gmail_refresh_token = None
        self.save()


class UserBankConfig(models.Model):
    """
    User's bank integration settings and preferences
    Supports both predefined banks and custom banks
    """
    SUPPORTED_BANKS = [
        ('tpbank', 'TPBank'),
        ('vcb', 'Vietcombank'),  # Phase 2
        ('techcombank', 'Techcombank'),  # Phase 2
        ('bidv', 'BIDV'),  # Phase 2
        ('mbbank', 'MB Bank'),  # Phase 3
        ('acb', 'ACB'),  # Phase 3
        ('sacombank', 'Sacombank'),  # Phase 3
        ('custom', 'Custom Bank'),  # For user-defined banks
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bank_configs'
    )
    bank_code = models.CharField(max_length=50)  # Increased length for custom banks
    
    # Custom bank settings (for user-defined banks)
    custom_bank_name = models.CharField(max_length=100, blank=True, null=True,
                                       help_text="Custom bank display name")
    is_custom_bank = models.BooleanField(default=False,
                                        help_text="Whether this is a user-defined custom bank")
    
    # Integration settings
    is_enabled = models.BooleanField(default=False)
    account_suffix = models.CharField(max_length=10, blank=True, null=True, 
                                     help_text="Last 4 digits of account to match transactions")
    sync_start_date = models.DateField(null=True, blank=True, 
                                      help_text="Start syncing from this date")
    
    # Sync status
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_successful_sync = models.DateTimeField(null=True, blank=True)
    sync_error_count = models.IntegerField(default=0)
    last_sync_error = models.TextField(blank=True, null=True)
    
    # Email processing settings
    sender_email_pattern = models.CharField(max_length=255, blank=True, null=True,
                                          help_text="Email pattern to match bank emails")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'bank_code']
        verbose_name = _('User Bank Configuration')
        verbose_name_plural = _('User Bank Configurations')

    def __str__(self):
        status = "✅ Enabled" if self.is_enabled else "❌ Disabled"
        bank_display = self.get_bank_display_name()
        return f"{self.user.get_short_name()} - {bank_display}: {status}"

    @property
    def bank_name(self):
        return self.get_bank_display_name()

    def get_bank_display_name(self):
        """Get display name for the bank (custom or predefined)"""
        if self.is_custom_bank and self.custom_bank_name:
            return self.custom_bank_name
        
        # Try to get from predefined choices
        for code, name in self.SUPPORTED_BANKS:
            if code == self.bank_code:
                return name
        
        # Fallback to bank_code if not found
        return self.bank_code.upper()

    def get_default_sender_pattern(self):
        """Get default email sender pattern for each bank"""
        patterns = {
            'tpbank': 'tpbank@tpb.com.vn',
            'vcb': 'info@vietcombank.com.vn',
            'techcombank': 'marketing@techcombank.com.vn',
            'bidv': 'info@bidv.com.vn',
            'mbbank': 'info@mbbank.com.vn',
            'acb': 'info@acb.com.vn',
            'sacombank': 'info@sacombank.com',
        }
        return patterns.get(self.bank_code, '')

    def enable_integration(self):
        """Enable bank integration with default settings"""
        # For custom banks, sender pattern is required
        if self.is_custom_bank and not self.sender_email_pattern:
            raise ValueError("Sender email pattern is required for custom banks")
        
        # For predefined banks, set default pattern if not specified
        if not self.is_custom_bank and not self.sender_email_pattern:
            self.sender_email_pattern = self.get_default_sender_pattern()
        
        if not self.sync_start_date:
            # Default to 30 days ago
            self.sync_start_date = timezone.now().date() - timedelta(days=30)
        
        self.is_enabled = True
        self.sync_error_count = 0
        self.last_sync_error = None
        self.save()

    def disable_integration(self):
        """Disable bank integration"""
        self.is_enabled = False
        self.save()

    @classmethod
    def create_custom_bank(cls, user, bank_name: str, sender_pattern: str, account_suffix: str = None):
        """Create a custom bank configuration"""
        # Generate unique bank_code for custom bank
        base_code = bank_name.lower().replace(' ', '').replace('-', '')[:20]
        bank_code = f"custom_{base_code}"
        
        # Ensure uniqueness
        counter = 1
        original_code = bank_code
        while cls.objects.filter(user=user, bank_code=bank_code).exists():
            bank_code = f"{original_code}_{counter}"
            counter += 1
        
        # Create custom bank config
        bank_config = cls.objects.create(
            user=user,
            bank_code=bank_code,
            custom_bank_name=bank_name,
            is_custom_bank=True,
            sender_email_pattern=sender_pattern,
            account_suffix=account_suffix,
            is_enabled=False  # User needs to explicitly enable
        )
        
        return bank_config


class BankEmailTransaction(models.Model):
    """
    Processed bank email transactions
    
    NOTE: We do NOT store raw email content for privacy
    Only essential transaction data matching existing Transaction model format
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bank_email_transactions'
    )
    bank_config = models.ForeignKey(
        'UserBankConfig',
        on_delete=models.CASCADE,
        related_name='email_transactions'
    )
    
    # Email metadata (minimal)
    email_message_id = models.CharField(max_length=255, unique=True, 
                                       help_text="Gmail message ID for deduplication")
    email_date = models.DateTimeField(help_text="Date email was received")
    email_subject = models.CharField(max_length=255, blank=True, null=True)
    
    # Transaction data (matches Transaction model format exactly)
    transaction_type = models.CharField(max_length=20, choices=Transaction.TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, 
                                help_text="Positive for income/investment, negative for expense")
    description = models.CharField(max_length=255)
    date = models.DateField(help_text="Transaction date (parsed from email)")
    expense_category = models.CharField(max_length=50, blank=True, null=True, 
                                       choices=Transaction.EXPENSE_CATEGORIES)
    
    # AI parsing metadata
    ai_confidence = models.FloatField(default=0.0, 
                                     help_text="AI confidence score (0.0-1.0)")
    parsing_method = models.CharField(max_length=20, default='gemini',
                                     choices=[('gemini', 'Gemini AI'), ('regex', 'Regex')])
    
    # Processing status
    is_processed = models.BooleanField(default=False, 
                                      help_text="Whether converted to Transaction")
    processed_at = models.DateTimeField(null=True, blank=True)
    transaction_id = models.ForeignKey('Transaction', on_delete=models.SET_NULL, 
                                      null=True, blank=True,
                                      help_text="Created Transaction if processed")
    
    # Error handling
    processing_error = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Bank Email Transaction')
        verbose_name_plural = _('Bank Email Transactions')
        ordering = ['-email_date', '-created_at']

    def __str__(self):
        return f"{self.bank_config.bank_code.upper()} - {self.description}: {self.amount:,.0f}₫ ({self.email_date.strftime('%Y-%m-%d')})"

    def process_to_transaction(self):
        """Convert bank email transaction to regular Transaction"""
        if self.is_processed:
            return self.transaction_id
        
        try:
            # Create Transaction with exact same format as AI chat
            transaction = Transaction.objects.create(
                user=self.user,
                transaction_type=self.transaction_type,
                amount=self.amount,
                description=f"[{self.bank_config.bank_code.upper()}] {self.description}",
                date=self.date,
                expense_category=self.expense_category,
                ai_confidence=self.ai_confidence,
                # Add bank source indicator
                notes=f"Auto-imported from {self.bank_config.bank_name} email"
            )
            
            # Mark as processed
            self.is_processed = True
            self.processed_at = timezone.now()
            self.transaction_id = transaction
            self.save()
            
            return transaction
            
        except Exception as e:
            self.processing_error = str(e)
            self.retry_count += 1
            self.save()
            raise

    @property
    def can_retry_processing(self):
        """Check if transaction can be retried for processing"""
        return not self.is_processed and self.retry_count < 3 