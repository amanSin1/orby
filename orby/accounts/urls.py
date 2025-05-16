from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add_meeting/', views.add_meeting, name='add_meeting'),
    
    # Chatbot frontend page
    path('chatbot_page/', views.chatbot_page, name='chatbot_page'),

    # Chatbot AJAX POST endpoint
    path('chatbot/', views.chatbot, name='chatbot'),
]
