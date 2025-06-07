from django.shortcuts import render
from django.http import JsonResponse


def placeholder_view(request):
    """Placeholder view for AI chat - will be implemented in Phase 5"""
    return JsonResponse({
        'status': 'Phase 1 Complete', 
        'message': 'AI Chat endpoints will be implemented in Phase 5'
    }) 