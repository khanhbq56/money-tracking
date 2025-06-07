"""
Health check views for deployment monitoring
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import os

def health_check(request):
    """Health check endpoint for Railway deployment"""
    db_status = "healthy"
    env_status = "healthy"
    
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        # Don't fail health check for database issues during startup
        db_status = f"warning: {str(e)}"
    
    # Check if required environment variables are set
    required_vars = ['SECRET_KEY']
    for var in required_vars:
        if not getattr(settings, var, None):
            env_status = f"missing {var}"
            break
    
    # Always return healthy for basic app functionality
    # Only fail if critical settings are missing
    is_healthy = env_status == "healthy"
    
    response_data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": db_status,
        "environment": env_status,
        "debug": settings.DEBUG,
        "version": "1.0.0",
        "app": "expense-tracker"
    }
    
    # Return 200 even with database warnings during startup
    status_code = 200 if is_healthy else 503
    return JsonResponse(response_data, status=status_code) 