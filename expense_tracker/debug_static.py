import os
from django.http import JsonResponse
from django.conf import settings

def debug_static_files(request):
    """Debug view to check static files"""
    static_root = settings.STATIC_ROOT
    staticfiles_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None
    
    response_data = {
        'static_root': str(static_root),
        'static_root_exists': os.path.exists(static_root),
        'staticfiles_dirs': [str(d) for d in settings.STATICFILES_DIRS],
        'static_url': settings.STATIC_URL,
        'debug': settings.DEBUG,
    }
    
    # Check if static files exist
    if os.path.exists(static_root):
        response_data['static_root_contents'] = os.listdir(static_root)
        
        js_dir = os.path.join(static_root, 'js')
        if os.path.exists(js_dir):
            response_data['js_files'] = os.listdir(js_dir)
        
        css_dir = os.path.join(static_root, 'css')
        if os.path.exists(css_dir):
            response_data['css_files'] = os.listdir(css_dir)
    
    # Check source static files
    if staticfiles_dir and os.path.exists(staticfiles_dir):
        response_data['source_static_contents'] = os.listdir(staticfiles_dir)
        
        source_js_dir = os.path.join(staticfiles_dir, 'js')
        if os.path.exists(source_js_dir):
            response_data['source_js_files'] = os.listdir(source_js_dir)
    
    return JsonResponse(response_data, indent=2) 