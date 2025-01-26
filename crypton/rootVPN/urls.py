# capitals/urls.py
from django.urls import path

from . import views
from .utils.email_sender import *

urlpatterns = [
    path('api/register/', views.UserRegistrationView.as_view()),
    path('api/login/', views.UserLoginView.as_view(), name='user-login'), 
    path('api/user_info/', views.UserInfoView.as_view(), name='user-login'), 
    path('send-verification-email/', send_verification_email, name='send_verification_email'),
    path('verify-email/', verify_email, name='verify_email'),  
]