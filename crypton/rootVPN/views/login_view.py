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


class UserLoginView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        device_id = request.data.get('device_id')
        device_type = request.data.get('device_type')
        # Получаем заголовок Authorization
        auth = request.META.get('HTTP_AUTHORIZATION')
        if not auth:
            return Response({"error": "Учетные данные не предоставлены"}, status=status.HTTP_401_UNAUTHORIZED)

        # Извлекаем и декодируем учетные данные
        try:
            auth_type, credentials = auth.split(' ')
            if auth_type != 'Basic':
                return Response({"error": "Неверный тип аутентификации"}, status=status.HTTP_401_UNAUTHORIZED)

            # Декодируем учетные данные
            decoded_credentials = base64.b64decode(credentials).decode('utf-8')
            email, password = decoded_credentials.split(':')
        except Exception as e:
            return Response({"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            print(email)
            user = UserVPN.objects.get(email=email)
        except UserVPN.DoesNotExist:
            return Response({"error": "Неверные учетные данные"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем правильность пароля
        if not check_password(password, user.password):
            return Response({"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        
        tariff = Tariff.objects.get(id= user.tariff_id if user.tariff_id!=None else 1)
        devices = Device.objects.filter(user_id=user.id)
        if devices.filter(device_id=device_id).exists():
            pass
        else:
            if tariff.max_number_of_devices>devices.count():
                device = Device(device_type = device_type, device_id = device_id, user = user)
                device.save()
            else:
                return Response({"error": "device_limit_over"}, status=status.HTTP_403_FORBIDDEN)
        # Генерируем токены
        token = create_token(user.id)
        # Возвращаем данные пользователя и токены
        return Response({
            'refresh_token': token,
            'access_token': token,
            'user': {
                'id': user.id,
                'email': user.email,
            }
        }, status=status.HTTP_200_OK)