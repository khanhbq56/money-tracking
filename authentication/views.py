import json
import logging
import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages

from .models import User

logger = logging.getLogger(__name__)


class GoogleOAuthInitView(View):
    """Initialize Google OAuth flow"""
    
    def get(self, request):
        # Check if OAuth is properly configured
        if not settings.GOOGLE_OAUTH2_CLIENT_ID or not settings.GOOGLE_OAUTH2_CLIENT_SECRET:
            logger.warning("Google OAuth not configured - redirecting to setup guide")
            return redirect('/?error=oauth_not_configured')
        
        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_OAUTH2_REDIRECT_URI]
                }
            },
            scopes=settings.GOOGLE_OAUTH2_SCOPES
        )
        
        flow.redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
        
        # Generate a random state value to prevent CSRF attacks
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='select_account'  # Force account selection for privacy
        )
        
        return HttpResponseRedirect(authorization_url)


class GoogleOAuthCallbackView(View):
    """Handle Google OAuth callback"""
    
    def get(self, request):
        try:
            # Check if OAuth is properly configured
            if not settings.GOOGLE_OAUTH2_CLIENT_ID or not settings.GOOGLE_OAUTH2_CLIENT_SECRET:
                logger.warning("Google OAuth not configured - redirecting to setup guide")
                return redirect('/?error=oauth_not_configured')
                
            # Check if this is Gmail OAuth callback (different state format)
            state = request.GET.get('state')
            if state and state.startswith('user_'):
                # This is Gmail OAuth callback, redirect to Gmail OAuth handler
                from django.urls import reverse
                gmail_callback_view = GmailOAuthCallbackView()
                return gmail_callback_view.get(request)
                
            # Verify state parameter to prevent CSRF attacks (for login OAuth)
            if state != request.session.get('oauth_state'):
                logger.warning("OAuth state mismatch - potential CSRF attack")
                return redirect('/?error=oauth_state_mismatch')
            
            # Handle authorization code
            code = request.GET.get('code')
            if not code:
                error = request.GET.get('error', 'unknown_error')
                logger.warning(f"OAuth authorization failed: {error}")
                return redirect(f'/?error=oauth_{error}')
            
            # Exchange authorization code for access token
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                        "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_OAUTH2_REDIRECT_URI]
                    }
                },
                scopes=settings.GOOGLE_OAUTH2_SCOPES,
                state=request.session.get('oauth_state')
            )
            
            flow.redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
            flow.fetch_token(authorization_response=request.build_absolute_uri())
            
            # Get user info from Google
            credentials = flow.credentials
            user_info = id_token.verify_oauth2_token(
                credentials.id_token,
                requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )
            
            # Get or create user
            user = self.get_or_create_user(user_info, request)
            
            # Log user in
            login(request, user)
            
            # Clean up session
            if 'oauth_state' in request.session:
                del request.session['oauth_state']
            
            logger.info(f"User {user.email} logged in successfully via Google OAuth")
            return redirect('/')
            
        except Exception as e:
            logger.error(f"OAuth callback error: {str(e)}")
            return redirect('/?error=oauth_callback_failed')
    
    def get_or_create_user(self, user_info, request):
        """Get or create user from Google user info"""
        google_id = user_info.get('sub')
        email = user_info.get('email')
        
        if not google_id or not email:
            raise ValueError("Missing required user information from Google")
        
        # Try to find existing user by Google ID or email
        user = None
        try:
            user = User.objects.get(google_id=google_id)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=email)
                # Link existing user to Google account
                user.google_id = google_id
                user.save()
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create_user(
                    username=email,  # Use email as username
                    email=email,
                    google_id=google_id,
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    profile_picture=user_info.get('picture', ''),
                    is_active=True
                )
        
        # Update user info and login tracking
        user.first_name = user_info.get('given_name', user.first_name)
        user.last_name = user_info.get('family_name', user.last_name) 
        user.profile_picture = user_info.get('picture', user.profile_picture)
        user.last_login_ip = self.get_client_ip(request)
        
        # Accept legal terms if not already accepted
        if not (user.privacy_policy_accepted and user.terms_accepted):
            user.accept_legal_terms(self.get_client_ip(request))
        else:
            user.save()
        
        return user
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class DemoLoginView(View):
    """Handle demo account login"""
    
    def post(self, request):
        try:
            # Parse request body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in demo login request: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': _('Invalid request format')
                }, status=400)
            
            legal_accepted = data.get('legal_accepted', False)
            
            if not legal_accepted:
                return JsonResponse({
                    'success': False,
                    'error': _('You must accept the terms and privacy policy')
                }, status=400)
            
            # Create or get demo user
            try:
                demo_user = self.create_demo_user(request)
                logger.info(f"Demo user created: {demo_user.username}")
            except Exception as e:
                logger.error(f"Failed to create demo user: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': _('Failed to create demo user account')
                }, status=500)
            
            # Accept legal terms
            try:
                if hasattr(demo_user, 'accept_legal_terms'):
                    demo_user.accept_legal_terms(self.get_client_ip(request))
                    logger.info(f"Legal terms accepted for demo user: {demo_user.username}")
                else:
                    # Fallback - just log the acceptance
                    logger.info(f"Legal terms accepted (fallback) for demo user: {demo_user.username}")
            except Exception as e:
                logger.error(f"Failed to accept legal terms for demo user {demo_user.username}: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': _('Failed to accept legal terms')
                }, status=500)
            
            # Set demo expiration
            try:
                if hasattr(demo_user, 'create_demo_expiration'):
                    demo_user.create_demo_expiration()
                    logger.info(f"Demo expiration set for user: {demo_user.username}")
                else:
                    # Fallback - no expiration for standard user
                    logger.info(f"Demo expiration skipped (fallback) for user: {demo_user.username}")
            except Exception as e:
                logger.error(f"Failed to set demo expiration for user {demo_user.username}: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': _('Failed to set demo expiration')
                }, status=500)
            
            # Log user in
            try:
                login(request, demo_user)
                logger.info(f"Demo user {demo_user.username} logged in successfully")
            except Exception as e:
                logger.error(f"Failed to log in demo user {demo_user.username}: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': _('Failed to log in demo user')
                }, status=500)
            
            return JsonResponse({
                'success': True,
                'message': _('Demo account created successfully'),
                'user': {
                    'username': demo_user.get_short_name() if hasattr(demo_user, 'get_short_name') else demo_user.first_name or demo_user.username,
                    'is_demo': getattr(demo_user, 'is_demo_user', True),
                    'expires_at': demo_user.demo_expires_at.isoformat() if hasattr(demo_user, 'demo_expires_at') and demo_user.demo_expires_at else None
                }
            })
            
        except Exception as e:
            logger.error(f"Unexpected error in demo login: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': _('Failed to create demo account')
            }, status=500)
    
    def create_demo_user(self, request):
        """Create a new demo user with sample data"""
        import uuid
        from django.db import transaction
        from django.contrib.auth import get_user_model
        
        # Generate unique demo user
        demo_username = f'demo_{uuid.uuid4().hex[:8]}'
        demo_email = f'{demo_username}@demo.local'
        
        try:
            with transaction.atomic():
                # Check if User model has custom fields
                User = get_user_model()
                has_custom_fields = hasattr(User, 'google_id') and hasattr(User, 'is_demo_user')
                
                if has_custom_fields:
                    # Use full custom User model
                    user = User.objects.create_user(
                        username=demo_username,
                        email=demo_email,
                        first_name=_('Demo User'),
                        is_demo_user=True,
                        is_active=True,
                        last_login_ip=self.get_client_ip(request)
                    )
                    logger.info(f"Created demo user with custom fields: {user.username}")
                else:
                    # Fallback to standard Django User
                    user = User.objects.create_user(
                        username=demo_username,
                        email=demo_email,
                        first_name=_('Demo User'),
                        is_active=True
                    )
                    logger.info(f"Created demo user with standard fields: {user.username}")
                
                # Add sample transaction data
                try:
                    self.create_sample_transactions(user)
                    logger.info(f"Created sample transactions for demo user: {user.username}")
                except Exception as e:
                    logger.error(f"Failed to create sample transactions for demo user {user.username}: {str(e)}")
                    # Don't fail the whole process, just skip sample data
                    pass
                
                return user
                
        except Exception as e:
            logger.error(f"Failed to create demo user in database: {str(e)}", exc_info=True)
            raise
    
    def create_sample_transactions(self, user):
        """Create sample transactions for demo user"""
        from transactions.models import Transaction
        from datetime import date, timedelta
        import random
        
        # Sample data for demo
        sample_expenses = [
            {'amount': 45000, 'description': _('Coffee and breakfast'), 'category': 'coffee'},
            {'amount': 120000, 'description': _('Lunch at restaurant'), 'category': 'food'},
            {'amount': 25000, 'description': _('Bus fare'), 'category': 'transport'},
            {'amount': 300000, 'description': _('Groceries'), 'category': 'shopping'},
            {'amount': 150000, 'description': _('Movie tickets'), 'category': 'entertainment'},
        ]
        
        sample_savings = [
            {'amount': 500000, 'description': _('Monthly savings')},
            {'amount': 200000, 'description': _('Emergency fund')},
        ]
        
        sample_investments = [
            {'amount': 1000000, 'description': _('Stock investment')},
            {'amount': 300000, 'description': _('Gold purchase')},
        ]
        
        base_date = date.today()
        
        try:
            # Create sample expenses
            for i, expense in enumerate(sample_expenses):
                Transaction.objects.create(
                    user=user,
                    transaction_type='expense',
                    amount=-abs(expense['amount']),  # Negative for expenses
                    description=expense['description'],
                    expense_category=expense['category'],
                    date=base_date - timedelta(days=random.randint(0, 30)),
                    ai_confidence=0.9
                )
            
            # Create sample savings
            for i, saving in enumerate(sample_savings):
                Transaction.objects.create(
                    user=user,
                    transaction_type='saving',
                    amount=saving['amount'],
                    description=saving['description'],
                    date=base_date - timedelta(days=random.randint(0, 15)),
                    ai_confidence=0.9
                )
            
            # Create sample investments
            for i, investment in enumerate(sample_investments):
                Transaction.objects.create(
                    user=user,
                    transaction_type='investment',
                    amount=investment['amount'],
                    description=investment['description'],
                    date=base_date - timedelta(days=random.randint(0, 20)),
                    ai_confidence=0.9
                )
                
        except Exception as e:
            logger.error(f"Error creating sample transactions: {str(e)}", exc_info=True)
            raise
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@require_http_methods(["POST"])
@csrf_exempt
def logout_view(request):
    """Handle user logout"""
    from django.contrib.auth import logout
    
    logout(request)
    return JsonResponse({
        'success': True,
        'message': _('Logged out successfully')
    })


# Legal Compliance Views
def privacy_policy_view(request):
    """Display privacy policy page"""
    from django.utils import translation
    from django.shortcuts import render
    
    # Handle language switching
    lang = request.GET.get('lang')
    if lang in ['vi', 'en']:
        translation.activate(lang)
        request.session['django_language'] = lang
    else:
        # Check if there's a language preference in session or cookie
        session_lang = request.session.get('django_language')
        cookie_lang = request.COOKIES.get('django_language')
        preferred_lang = session_lang or cookie_lang or 'vi'
        
        if preferred_lang in ['vi', 'en']:
            translation.activate(preferred_lang)
        else:
            translation.activate('vi')
    
    context = {
        'last_updated': '2024-01-15'
    }
    
    response = render(request, 'legal/privacy_policy.html', context)
    
    # Set language cookie if changed
    if lang in ['vi', 'en']:
        response.set_cookie('django_language', lang, max_age=365*24*60*60)
    
    return response


def terms_of_service_view(request):
    """Display terms of service page"""
    from django.utils import translation
    from django.shortcuts import render
    
    # Handle language switching
    lang = request.GET.get('lang')
    if lang in ['vi', 'en']:
        translation.activate(lang)
        request.session['django_language'] = lang
    else:
        # Check if there's a language preference in session or cookie
        session_lang = request.session.get('django_language')
        cookie_lang = request.COOKIES.get('django_language')
        preferred_lang = session_lang or cookie_lang or 'vi'
        
        if preferred_lang in ['vi', 'en']:
            translation.activate(preferred_lang)
        else:
            translation.activate('vi')
    
    context = {
        'last_updated': '2024-01-15'
    }
    
    response = render(request, 'legal/terms_of_service.html', context)
    
    # Set language cookie if changed
    if lang in ['vi', 'en']:
        response.set_cookie('django_language', lang, max_age=365*24*60*60)
    
    return response


@require_http_methods(["GET"])
def session_status_view(request):
    """Check session status and demo expiration"""
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False}, status=401)
    
    data = {
        'authenticated': True,
        'user_id': request.user.id,
        'username': request.user.get_short_name(),
        'is_demo': getattr(request.user, 'is_demo_user', False),
    }
    
    # Add demo expiration info if applicable
    if hasattr(request.user, 'is_demo_user') and request.user.is_demo_user:
        if hasattr(request.user, 'demo_expires_at') and request.user.demo_expires_at:
            data['demo_expires_at'] = request.user.demo_expires_at.isoformat()
            data['demo_expired'] = request.user.is_demo_expired()
    
    return JsonResponse(data)


@login_required
def settings_view(request):
    """Render settings page - Foundation for bank integration"""
    context = {
        'user': request.user,
        'page_title': _('Settings'),
    }
    return render(request, 'settings.html', context) 


# =============================================================================
# SEPARATE GMAIL OAUTH FOR BANK INTEGRATION (Phase 1)
# =============================================================================

# Separate Gmail OAuth scopes for bank integration (read-only emails)
BANK_GMAIL_OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
]

class GmailOAuthInitiateView(APIView):
    """
    Initiate separate Gmail OAuth flow for bank integration
    
    CRITICAL: This is separate from login OAuth
    - Login OAuth: Profile info only (existing GoogleOAuthInitView)  
    - Bank Gmail OAuth: Read emails only (this view)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Initiate Gmail OAuth for bank integration"""
        try:
            # Check if there's a bank parameter for auto-enable after OAuth
            bank_to_enable = request.GET.get('bank')
            if bank_to_enable:
                request.session['pending_bank_enable'] = bank_to_enable
            
            # Create OAuth flow with Gmail read-only scope
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [f"{settings.SITE_URL}/auth/google/callback/"]
                    }
                },
                scopes=BANK_GMAIL_OAUTH_SCOPES
            )
            
            # Set redirect URI (reuse login OAuth callback)
            flow.redirect_uri = f"{settings.SITE_URL}/auth/google/callback/"
            
            # Generate authorization URL with user context
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='false',  # Only request Gmail scopes
                prompt='consent',  # Force consent to get refresh token
                state=f"user_{request.user.id}",  # Include user ID in state
            )
            
            # Store state in session for verification
            request.session['gmail_oauth_state'] = state
            
            # Log Gmail OAuth initiation
            logger.info(f"Gmail OAuth initiated for user {request.user.email}")
            
            return redirect(authorization_url)
            
        except Exception as e:
            logger.error(f"Gmail OAuth initiation error: {str(e)}")
            messages.error(request, 'Failed to initiate Gmail permission request. Please try again.')
            return redirect('/settings/#bank-integration')


class GmailOAuthCallbackView(APIView):
    """
    Handle Gmail OAuth callback for bank integration
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Handle Gmail OAuth callback"""
        try:
            # Get authorization code and state
            code = request.GET.get('code')
            state = request.GET.get('state')
            error = request.GET.get('error')
            
            # Check for OAuth errors
            if error:
                logger.warning(f"Gmail OAuth error: {error}")
                messages.error(request, f'Gmail permission denied: {error}')
                return redirect('/settings/#bank-integration')
            
            if not code:
                logger.warning("Gmail OAuth callback missing authorization code")
                messages.error(request, 'Missing authorization code. Please try again.')
                return redirect('/settings/#bank-integration')
            
            # Verify state parameter
            session_state = request.session.get('gmail_oauth_state')
            if not session_state or session_state != state:
                logger.warning(f"Gmail OAuth state mismatch: {state} vs {session_state}")
                messages.error(request, 'Invalid state parameter. Please try again.')
                return redirect('/settings/#bank-integration')
            
            # Verify user from state
            if not state.startswith(f"user_{request.user.id}"):
                logger.warning(f"Gmail OAuth user mismatch in state: {state}")
                messages.error(request, 'User verification failed. Please try again.')
                return redirect('/settings/#bank-integration')
            
            # Exchange authorization code for tokens
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [f"{settings.SITE_URL}/auth/google/callback/"]
                    }
                },
                scopes=BANK_GMAIL_OAUTH_SCOPES,
                state=state
            )
            flow.redirect_uri = f"{settings.SITE_URL}/auth/google/callback/"
            
            # Get token
            flow.fetch_token(code=code)
            
            # Store Gmail permission and tokens
            self.store_gmail_permission(request.user, flow.credentials)
            
            # Clean up session
            if 'gmail_oauth_state' in request.session:
                del request.session['gmail_oauth_state']
            
            # Success message
            messages.success(request, '✅ Gmail permission granted successfully! You can now enable bank integrations.')
            logger.info(f"Gmail OAuth completed successfully for user {request.user.email}")
            
            # Check if there's a pending bank to enable from session
            pending_bank = request.session.get('pending_bank_enable')
            if pending_bank:
                # Clean up session
                del request.session['pending_bank_enable']
                # Redirect with bank parameter to auto-enable
                return redirect(f'/settings/?enable_bank={pending_bank}#bank-integration')
            
            return redirect('/settings/#bank-integration')
            
        except Exception as e:
            logger.error(f"Gmail OAuth callback error: {str(e)}")
            messages.error(request, 'Failed to process Gmail permission. Please try again.')
            return redirect('/settings/#bank-integration')
    
    def store_gmail_permission(self, user, credentials):
        """Store Gmail OAuth tokens for bank integration"""
        from transactions.models import UserGmailPermission
        
        # Get or create Gmail permission record
        gmail_permission, created = UserGmailPermission.objects.get_or_create(
            user=user,
            defaults={
                'has_gmail_permission': True,
                'permission_granted_at': timezone.now(),
            }
        )
        
        # Update with new tokens
        gmail_permission.gmail_oauth_token = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
        }
        # Handle timezone for expiry (credentials.expiry might be naive)
        if credentials.expiry:
            if credentials.expiry.tzinfo is None:
                # Make it timezone-aware
                gmail_permission.gmail_token_expires_at = timezone.make_aware(credentials.expiry)
            else:
                gmail_permission.gmail_token_expires_at = credentials.expiry
        else:
            gmail_permission.gmail_token_expires_at = None
        gmail_permission.gmail_refresh_token = credentials.refresh_token
        gmail_permission.has_gmail_permission = True
        gmail_permission.permission_granted_at = timezone.now()
        gmail_permission.permission_last_used = timezone.now()
        
        gmail_permission.save()
        
        logger.info(f"Gmail permission stored for user {user.email}")


class GmailPermissionRevokeView(APIView):
    """
    Revoke Gmail permission for bank integration
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Revoke Gmail permission"""
        try:
            from transactions.models import UserGmailPermission, UserBankConfig
            
            # Get Gmail permission
            try:
                gmail_permission = UserGmailPermission.objects.get(user=request.user)
            except UserGmailPermission.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'No Gmail permission found'
                }, status=404)
            
            # Disable all bank integrations first
            UserBankConfig.objects.filter(user=request.user).update(is_enabled=False)
            
            # Revoke permission
            gmail_permission.revoke_permission()
            
            logger.info(f"Gmail permission revoked for user {request.user.email}")
            
            return JsonResponse({
                'success': True,
                'message': 'Gmail permission revoked successfully'
            })
            
        except Exception as e:
            logger.error(f"Gmail permission revoke error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to revoke Gmail permission'
            }, status=500)


# =============================================================================
# BANK INTEGRATION API ENDPOINTS (Phase 1)
# =============================================================================

class BankIntegrationStatusView(APIView):
    """
    Get bank integration status for current user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all bank integration statuses"""
        try:
            from transactions.models import UserBankConfig
            
            statuses = {}
            
            # Get all bank configurations for user
            bank_configs = UserBankConfig.objects.filter(user=request.user)
            
            for config in bank_configs:
                statuses[config.bank_code] = {
                    'enabled': config.is_enabled,
                    'last_sync': config.last_sync_at.isoformat() if config.last_sync_at else None,
                    'last_successful_sync': config.last_successful_sync.isoformat() if config.last_successful_sync else None,
                    'sync_error_count': config.sync_error_count,
                    'last_sync_error': config.last_sync_error,
                }
            
            return JsonResponse(statuses)
            
        except Exception as e:
            logger.error(f"Bank integration status error: {str(e)}")
            return JsonResponse({
                'error': 'Failed to get bank integration status'
            }, status=500)


class BankIntegrationEnableView(APIView):
    """
    Enable bank integration for a specific bank
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Enable bank integration"""
        try:
            from transactions.models import UserBankConfig, UserGmailPermission
            
            bank_code = request.data.get('bank_code')
            if not bank_code:
                return JsonResponse({
                    'success': False,
                    'error': 'Bank code is required'
                }, status=400)
            
            # Check if Gmail permission exists
            try:
                gmail_permission = UserGmailPermission.objects.get(user=request.user)
                if not gmail_permission.has_gmail_permission:
                    return JsonResponse({
                        'success': False,
                        'error': 'Gmail permission required'
                    }, status=403)
            except UserGmailPermission.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Gmail permission required'
                }, status=403)
            
            # Get or create bank configuration
            bank_config, created = UserBankConfig.objects.get_or_create(
                user=request.user,
                bank_code=bank_code,
                defaults={
                    'is_enabled': True,
                }
            )
            
            if not created:
                # Enable existing configuration
                bank_config.enable_integration()
            else:
                # Set up new configuration
                bank_config.enable_integration()
            
            logger.info(f"Bank integration enabled: {bank_code} for user {request.user.email}")
            
            return JsonResponse({
                'success': True,
                'message': f'{bank_code.upper()} integration enabled successfully',
                'last_sync': bank_config.last_sync_at.isoformat() if bank_config.last_sync_at else None,
            })
            
        except Exception as e:
            logger.error(f"Bank integration enable error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to enable bank integration'
            }, status=500)


class BankIntegrationDisableView(APIView):
    """
    Disable bank integration for a specific bank
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Disable bank integration"""
        try:
            from transactions.models import UserBankConfig
            
            bank_code = request.data.get('bank_code')
            if not bank_code:
                return JsonResponse({
                    'success': False,
                    'error': 'Bank code is required'
                }, status=400)
            
            # Get bank configuration
            try:
                bank_config = UserBankConfig.objects.get(
                    user=request.user,
                    bank_code=bank_code
                )
                bank_config.disable_integration()
                
                logger.info(f"Bank integration disabled: {bank_code} for user {request.user.email}")
                
                return JsonResponse({
                    'success': True,
                    'message': f'{bank_code.upper()} integration disabled'
                })
                
            except UserBankConfig.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Bank configuration not found'
                }, status=404)
            
        except Exception as e:
            logger.error(f"Bank integration disable error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to disable bank integration'
            }, status=500)


class GmailPermissionStatusView(APIView):
    """
    Check Gmail permission status for current user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check if user has Gmail permission"""
        try:
            from transactions.models import UserGmailPermission
            
            try:
                gmail_permission = UserGmailPermission.objects.get(user=request.user)
                
                # Try to refresh token if expired
                token_valid = gmail_permission.refresh_token_if_needed()
                
                has_permission = (
                    gmail_permission.has_gmail_permission and 
                    token_valid
                )
                
                return JsonResponse({
                    'has_permission': has_permission,
                    'granted_at': gmail_permission.permission_granted_at.isoformat() if gmail_permission.permission_granted_at else None,
                    'last_used': gmail_permission.permission_last_used.isoformat() if gmail_permission.permission_last_used else None,
                    'token_expired': gmail_permission.is_token_expired(),
                })
                
            except UserGmailPermission.DoesNotExist:
                return JsonResponse({
                    'has_permission': False,
                    'granted_at': None,
                    'last_used': None,
                    'token_expired': True,
                })
            
        except Exception as e:
            logger.error(f"Gmail permission status error: {str(e)}")
            return JsonResponse({
                'has_permission': False,
                'error': 'Failed to check Gmail permission status'
            }, status=500) 