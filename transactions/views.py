from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    """Main app view - placeholder for Phase 3"""
    return HttpResponse(
        "<h1>Expense Tracker</h1>"
        "<p>Phase 1 Complete! Frontend will be implemented in Phase 3.</p>"
        "<p><a href='/admin/'>Go to Admin</a></p>"
    ) 