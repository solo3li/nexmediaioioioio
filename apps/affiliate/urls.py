from django.urls import path
from . import views

urlpatterns = [
    path('', views.affiliate_dashboard_view, name='affiliate_dashboard'),
]
