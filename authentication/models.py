from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model with Google OAuth and demo account support
    """
    # Override email to be unique and required
    email = models.EmailField(
        unique=True,
        verbose_name=_('Email address')
    )
    
    # Google OAuth integration
    google_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name=_('Google ID')
    )
    
    # Account type
    is_demo_user = models.BooleanField(
        default=False,
        verbose_name=_('Is Demo User'),
        help_text=_('Designates whether this is a temporary demo account.')
    )
    
    # Profile information (minimal from Google)
    profile_picture = models.URLField(
        blank=True,
        verbose_name=_('Profile Picture URL')
    )
    
    # Legal consent tracking
    privacy_policy_accepted = models.BooleanField(
        default=False,
        verbose_name=_('Privacy Policy Accepted')
    )
    privacy_policy_accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Privacy Policy Accepted At')
    )
    terms_accepted = models.BooleanField(
        default=False,
        verbose_name=_('Terms Accepted')
    )
    terms_accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Terms Accepted At')
    )
    
    # Session and security tracking
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Last Login IP')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    # Demo account expiration
    demo_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Demo Account Expires At'),
        help_text=_('Demo accounts expire after 24 hours')
    )
    
    # Use email as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'auth_user'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]
    
    def is_demo_expired(self):
        """Check if demo account has expired"""
        if not self.is_demo_user or not self.demo_expires_at:
            return False
        return timezone.now() > self.demo_expires_at
    
    def accept_legal_terms(self, request_ip=None):
        """Mark legal terms as accepted"""
        now = timezone.now()
        self.privacy_policy_accepted = True
        self.privacy_policy_accepted_at = now
        self.terms_accepted = True
        self.terms_accepted_at = now
        if request_ip:
            self.last_login_ip = request_ip
        self.save(update_fields=[
            'privacy_policy_accepted', 'privacy_policy_accepted_at',
            'terms_accepted', 'terms_accepted_at', 'last_login_ip'
        ])
    
    def create_demo_expiration(self):
        """Set demo account to expire in 24 hours"""
        if self.is_demo_user:
            self.demo_expires_at = timezone.now() + timezone.timedelta(hours=24)
            self.save(update_fields=['demo_expires_at']) 