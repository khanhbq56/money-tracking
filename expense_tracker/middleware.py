"""
Custom middleware for Railway deployment
"""

class HealthCheckMiddleware:
    """Middleware to handle health check requests without SSL redirect"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip SSL redirect for health check endpoints
        if request.path in ['/health/', '/health']:
            request.is_health_check = True
        
        response = self.get_response(request)
        return response


class RailwayMiddleware:
    """Middleware for Railway-specific handling"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add Railway-specific headers
        if hasattr(request, 'META'):
            # Handle Railway health checks
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            if 'RailwayHealthCheck' in user_agent:
                request.is_railway_health_check = True
        
        response = self.get_response(request)
        return response 