import json
import logging
import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import login
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

from .models import User

logger = logging.getLogger(__name__)


class GoogleOAuthInitView(View):
    """Initialize Google OAuth flow"""
    
    def get(self, request):
        # Check if we're in development mode
        if settings.GOOGLE_OAUTH2_CLIENT_ID == 'development-client-id':
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
            # Check if we're in development mode
            if settings.GOOGLE_OAUTH2_CLIENT_ID == 'development-client-id':
                logger.warning("Google OAuth not configured - redirecting to setup guide")
                return redirect('/?error=oauth_not_configured')
                
            # Verify state parameter to prevent CSRF attacks
            if request.GET.get('state') != request.session.get('oauth_state'):
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
                demo_user.accept_legal_terms(self.get_client_ip(request))
                logger.info(f"Legal terms accepted for demo user: {demo_user.username}")
            except Exception as e:
                logger.error(f"Failed to accept legal terms for demo user {demo_user.username}: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'error': _('Failed to accept legal terms')
                }, status=500)
            
            # Set demo expiration
            try:
                demo_user.create_demo_expiration()
                logger.info(f"Demo expiration set for user: {demo_user.username}")
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
                    'username': demo_user.get_short_name(),
                    'is_demo': True,
                    'expires_at': demo_user.demo_expires_at.isoformat() if demo_user.demo_expires_at else None
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
        
        # Generate unique demo user
        demo_username = f'demo_{uuid.uuid4().hex[:8]}'
        demo_email = f'{demo_username}@demo.local'
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=demo_username,
                    email=demo_email,
                    first_name=_('Demo User'),
                    is_demo_user=True,
                    is_active=True,
                    last_login_ip=self.get_client_ip(request)
                )
                logger.info(f"Created demo user: {user.username}")
                
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
    # Handle language switching
    from django.utils import translation
    from django.conf import settings
    
    lang = request.GET.get('lang')
    if lang in ['vi', 'en']:
        translation.activate(lang)
        # Use the correct session key
        request.session['django_language'] = lang
    else:
        # Check if there's a language preference in session
        session_lang = request.session.get('django_language', 'vi')
        translation.activate(session_lang)
    
    context = {
        'last_updated': '2024-01-15'
    }
    return render(request, 'legal/privacy_policy.html', context)


def terms_of_service_view(request):
    """Display terms of service page"""
    # Handle language switching
    from django.utils import translation
    from django.conf import settings
    
    lang = request.GET.get('lang')
    if lang in ['vi', 'en']:
        translation.activate(lang)
        # Use the correct session key
        request.session['django_language'] = lang
    else:
        # Check if there's a language preference in session
        session_lang = request.session.get('django_language', 'vi')
        translation.activate(session_lang)
    
    context = {
        'last_updated': '2024-01-15'
    }
    return render(request, 'legal/terms_of_service.html', context) 