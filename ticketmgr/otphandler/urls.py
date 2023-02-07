from django.urls import path
from . import views

urlpatterns = [
    path('ticket/new', views.ticket_new, name='ticket_new'),
    path('ticket/auth', views.ticket_auth, name='ticket_auth')
]
