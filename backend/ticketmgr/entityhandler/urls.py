from . import views
from django.urls import path

urlpatterns = [
    path('login', views.tkt_login, name='tkt_login'),
    path('logout', views.tkt_logout, name='tkt_logout'),
    path('user', views.user_signup, name='user_signup'),
    path('user/<str:username>', views.user_info, name='user_info'),
    path('user/<str:username>/event', views.user_events, name='user_events'),
    path('event', views.event, name='event'),
    path('event/<uuid:event_uuid>', views.event_info, name='event_info'),
    path('event/<uuid:event_uuid>/user', views.event_users, name='event_users'),
    path('event/<uuid:event_uuid>/agent', views.event_agents, name='event_agents'),
    path('event/<uuid:event_uuid>/admin', views.event_admins, name='event_admins')
]