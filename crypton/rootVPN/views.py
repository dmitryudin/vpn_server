from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from .serializers import ServerSerializer, UserRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserVPN, Server, Device, Tariff
from .utils.password_hasher import *
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication
import base64
from rest_framework.permissions import IsAuthenticated

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Генерируем токены
        refresh = RefreshToken.for_user(user)
        print('user_id from controller', user.id)
        # Формируем ответ с токенами
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'balance': user.balance
            }
        }, status=status.HTTP_201_CREATED)




class UserLoginView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        print('auth')
        # Получаем заголовок Authorization
        auth = request.META.get('HTTP_AUTHORIZATION')
        print(auth)

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
            user = UserVPN.objects.prefetch_related('devices', 'tariff', 'invitations').get(email=email)
            

            
        except UserVPN.DoesNotExist:
            return Response({"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        # Проверяем правильность пароля
        if not check_password(password, user.password):
            return Response({"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        # Генерируем токены
        refresh = RefreshToken.for_user(user)
        device_id = request.data.get('device_id')
        device_type = request.data.get('device_type')
        devices = user.devices.all()  # Все устройства пользователя
        tariff = user.tariff 

         # Проверяем, существует ли устройство с заданным device_id
        if devices.filter(device_id=device_id).exists():
            print("Устройство с таким device_id уже существует.")
            return
        
        # Проверяем, не превышает ли количество устройств 5
        if devices.count() >= 5:
            print("Количество устройств не может превышать 5.")
            return
        
        # Если устройство не существует и количество устройств меньше 5, добавляем новое устройство
        new_device = Device(device_type=device_type, device_id=device_id, user=user)
        new_device.save()
        print("Новое устройство добавлено:", new_device.device_id)
        
        
        

        # Возвращаем данные пользователя и токены
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
            }
        }, status=status.HTTP_200_OK)
    

    
class UserInfoView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  # Защита контроллера
    def get(self, request):
        try:
            email = request.query_params.get('email') 
            user = UserVPN.objects.get(email=email)
            servers = Server.objects.all()

            server_serializer = ServerSerializer(servers, many=True)
            user_info = {
                'balance': user.balance,
                'is_blocked': user.is_blocked
            }

            return Response({
                'servers': server_serializer.data,
                'user_info': user_info
            })
        except UserVPN.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)