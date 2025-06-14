from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from .models import User


class AuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle authentication and demo account expiration
    """
    
    def process_request(self, request):
        """Process request to check authentication and demo expiration"""
        
        # Skip authentication for static files, admin, and auth URLs
        skip_urls = [
            '/static/', '/media/', '/admin/', '/auth/', 
            '/health/', '/api/ai_chat/'
        ]
        
        if any(request.path.startswith(url) for url in skip_urls):
            return None
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if demo user has expired
            if hasattr(request.user, 'is_demo_user') and request.user.is_demo_user:
                if request.user.is_demo_expired():
                    logout(request)
                    # For AJAX requests, return JSON response
                    if request.headers.get('Content-Type') == 'application/json':
                        from django.http import JsonResponse
                        return JsonResponse({
                            'error': 'demo_expired',
                            'message': 'Demo session has expired. Please login again.'
                        }, status=401)
                    # For regular requests, redirect to home with error
                    return redirect('/?demo_expired=true')
        
        return None
    
    def process_response(self, request, response):
        """Process response to add authentication context"""
        
        # Skip for AJAX requests and non-HTML responses
        if (request.headers.get('Content-Type') == 'application/json' or 
            not response.get('Content-Type', '').startswith('text/html')):
            return response
        
        # Add authentication context to template context
        if hasattr(response, 'context_data'):
            response.context_data = response.context_data or {}
            response.context_data['user_authenticated'] = request.user.is_authenticated
            response.context_data['is_demo_user'] = (
                request.user.is_authenticated and 
                getattr(request.user, 'is_demo_user', False)
            )
            if request.user.is_authenticated and hasattr(request.user, 'demo_expires_at'):
                response.context_data['demo_expires_at'] = request.user.demo_expires_at
        
        return response 