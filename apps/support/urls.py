from django.urls import path
from . import views

urlpatterns = [
    path('', views.support_list_view, name='support_list'),
    path('<int:ticket_id>/', views.ticket_detail_view, name='ticket_detail'),
    path('<int:ticket_id>/events/', views.ticket_events_stream, name='ticket_events'),
]
