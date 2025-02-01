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



class ServerInfoView(generics.GenericAPIView):
    '''
    
    
    '''
    def get(self, request):
        try:
            servers = Server.objects.all()
            tariffs = Tariff.objects.all()
            tariff_serializer = TariffSerializer(tariffs, many=True)
            server_serializer = ServerSerializer(servers, many=True)
            
            return Response({
                'tariffs': tariff_serializer.data,
                'servers': server_serializer.data,
                
            })
        except UserVPN.DoesNotExist:
            return Response({'error': 'Неизвестная ошибка'}, status=status.HTTP_400_BAD_REQUEST)
        



        
