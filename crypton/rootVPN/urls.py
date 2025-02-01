# capitals/urls.py
from django.urls import path

from .views import email_confirm_view, login_view, registration_view, user_info_view, server_info_view
from .utils.email_sender import *

urlpatterns = [
    path('api/register/', registration_view.UserRegistrationView.as_view()),
    path('api/login/', login_view.UserLoginView.as_view(), name='user-login'), 
    path('api/user_info/', user_info_view.UserInfoView.as_view(), name='user-login'), 
    path('api/create_invite/', user_info_view.CreateInviteCodeView.as_view(), name='user-login'),
    path('send-verification-email/', send_verification_email, name='send_verification_email'),
    path('api/verify-email/', email_confirm_view.EmailConfirmView.as_view(), name='verify_email'), 
    path('api/free-servers/', server_info_view.ServerInfoView.as_view(), name='verify_email'), 
    
]