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
import datetime

def get_differance_datetime_in_days_with_now(last_datetime: datetime.datetime)->int:
    datetime_now = datetime.datetime.now()
    last_datetime = last_datetime.replace(tzinfo=None)
    # Вычисление разницы
    difference = datetime_now - last_datetime
    return difference.days


def carry_out_the_deduction(user: UserVPN)->None:
    if (user.last_payment==None):
        user.tariff_id = 1
        user.save()
        return
        
    if (get_differance_datetime_in_days_with_now(last_datetime=user.last_payment)>=1):
        if(user.balance>=1):
            user.balance = user.balance - 1
            user.last_payment = datetime.datetime.now()
            
        else:
            user.tariff_id = 1
        user.save()
            


class UserInfoView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]  # Защита контроллера
    # authentication_classes = [JWTAuthentication]  # Аутентификация с помощью JWT
    @jwt_required
    def get(self, request):
        
        email = request.query_params.get('email')
        
        try:
            email = request.query_params.get('email')
            print(email) 
            user = UserVPN.objects.get(email=email)
            carry_out_the_deduction(user=user)
            servers = Server.objects.all()
            tariffs = Tariff.objects.all()
            tariff_serializer = TariffSerializer(tariffs, many=True)
            server_serializer = ServerSerializer(servers, many=True)
            

            user_info = {
                'balance': user.balance,
                'is_blocked': user.is_blocked,
                'current_tarif_id': user.tariff_id,
                'is_email_verified':user.is_email_verified

            }

            return Response({
                'tariffs': tariff_serializer.data,
                'servers': server_serializer.data,
                'user_info': user_info
            })
        except UserVPN.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
        



        
class CreateInviteCodeView(generics.GenericAPIView):
    @jwt_required
    def post(self, request):
        try:
            # Генерация уникального кода приглашения из 6 случайных цифр
            code = ''.join(random.choices('0123456789', k=6))
            email = request.data.get('email')
            user = UserVPN.objects.get(email=email)
            
            # Создание объекта InviteCode и связывание с текущим пользователем
            invite_code = InviteCode.objects.create(code=code, user=user, balance=5)
            invite_code.save()
            return Response({
                'message': 'Код приглашения успешно создан',
                'invite_code': invite_code.code
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]  # Защита контроллера
    # authentication_classes = [JWTAuthentication]  # Аутентификация с помощью JWT
    @jwt_required
    def post(self, request):
        email = request.data.get('email')
        device_id = request.data.get('device_id')
        print('email = ', email)
        user = UserVPN.objects.get(email=email)
        device = Device.objects.get(device_id = device_id)
        if device.user_id == user.id:
            device.delete()
            return Response({'status':'success'}, status=status.HTTP_200_OK)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
