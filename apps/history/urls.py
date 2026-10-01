from django.urls import path
from . import views

urlpatterns = [
    path('api/generate/', views.generate_api, name='api_generate'),
    path('api/generation-status/<int:history_id>/', views.generation_status_api, name='api_generation_status'),
    path('api/user-history/', views.user_history_api, name='api_user_history'),
]
