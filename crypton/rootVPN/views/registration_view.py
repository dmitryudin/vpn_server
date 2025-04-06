from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from ..serializers.serializers import ServerSerializer, TariffSerializer, UserRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import UserVPN, Server, Device, Tariff, InviteCode
from ..utils.password_hasher import *
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication
import base64
import random
from ..utils.email_sender import send_verification_email, verify_email
import datetime
from ..utils.jwt_lib import jwt_required, create_token


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    def post(self, request, *args, **kwargs):
        if UserVPN.objects.filter(email=request.data['email'].lower()).exists():
           return Response({
        }, status=status.HTTP_409_CONFLICT)
      
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        invite_code = request.data.get('invite_code', None)
        if invite_code:
            try:
                # Находим код приглашения
                code_instance = InviteCode.objects.get(code=invite_code)
                # Зачисляем баланс пользователю, который создал код приглашения
                user_inviter = UserVPN.objects.get(id=code_instance.user_id)
                user_inviter.balance += code_instance.balance
                user_inviter.last_payment = datetime.datetime.now()
                user_inviter.save()

                # Удаляем код приглашения после использования
                code_instance.delete()
            except Exception as e:
                print(e)
        
        send_verification_email(user.id)
                
        # Генерируем токены
        token = create_token(user.id)
        print('user_id from controller', user.id)
        # Формируем ответ с токенами
        return Response({
            'refresh_token': token,
            'access_token': token,
            'user': {
                'email': user.email,
                'balance': user.balance
            }
        }, status=status.HTTP_201_CREATED)