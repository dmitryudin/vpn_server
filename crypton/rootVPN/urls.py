# capitals/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('api/register/', views.UserRegistrationView.as_view()),
    path('api/login/', views.UserLoginView.as_view(), name='user-login'), 
    path('api/user_info/', views.UserInfoView.as_view(), name='user-login'),   
]