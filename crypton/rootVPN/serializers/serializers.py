from rest_framework import serializers
from ..models import UserVPN, Server, Device, Tariff
from ..utils.password_hasher import *
from ..utils.telegram_bot import *




class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ['id', 'name', 'url', 'ip', 'username', 'country', 'load_coef', 'password']

class UserVPNSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVPN
        fields = ['balance', 'is_blocked']



class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ('id', 'name', 'descryption', 'days', 'cost', 'max_number_of_devices')

class UserRegistrationSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField()
    device_id = serializers.CharField()
    
    class Meta:
        model = UserVPN
        fields = ('email', 'password', 'device_type', 'device_id')
        extra_kwargs = {'extra': {'allow_extra_fields': True}}  # Игнорировать лишние поля


 

    

    def create(self, validated_data):
        
        user = UserVPN(
            password= hash_password(validated_data['password']),
            email=validated_data['email'],
            balance = 0.0,
            tariff_id = 1,
            is_email_verified = False
        )
        user.save()
        device = Device(device_type = validated_data['device_type'], device_id = validated_data['device_id'], user = user)
        device.save()
        
        return user

