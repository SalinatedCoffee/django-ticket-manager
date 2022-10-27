from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.user_signup, name='user_signup'),
    path('user/<str:username>', views.user_info, name='user_info'),
    path('user/<str:username>/events', views.user_events, name='user_events'),
    path('event/new', views.event_new, name='event_new'),
    path('event/list', views.event_query, name='event_query'),
    path('event/<int:event_id>', views.event_info, name='event_info'),
    path('event/<int:event_id>/users', views.event_users, name='event_users'),
    path('event/<int:event_id>/agents', views.event_agents, name='event_agents'),
    path('event/<int:event_id>/admins', views.event_admins, name='event_admins')
]