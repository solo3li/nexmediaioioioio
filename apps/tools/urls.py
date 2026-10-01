from django.urls import path
from . import views

urlpatterns = [
    path('', views.studio_redirect, name='studio'),
    path('<slug:tool_slug>/', views.studio_tool_view, name='studio_tool'),
]
