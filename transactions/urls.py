from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Main page view (for template rendering)
    path('', views.index, name='index'),
] 