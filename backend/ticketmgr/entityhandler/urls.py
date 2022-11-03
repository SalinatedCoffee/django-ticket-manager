from . import views
from django.urls import path

urlpatterns = [
    path('user', views.user_signup, name='user_signup'),
    path('user/<str:username>', views.user_info, name='user_info'),
    path('user/<str:username>/events', views.user_events, name='user_events'),
    path('event/', views.events, name='events'),
    path('event/<int:event_id>', views.event_info, name='event_info'),
    path('event/<int:event_id>/users', views.event_users, name='event_users'),
    path('event/<int:event_id>/agents', views.event_agents, name='event_agents'),
    path('event/<int:event_id>/admins', views.event_admins, name='event_admins')
]