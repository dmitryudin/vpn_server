from rest_framework import serializers
from .models import UserVPN, Server, Device, Tariff
from .utils.password_hasher import *
from .utils.telegram_bot import *




class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ['id', 'name', 'url', 'ip', 'username', 'country', 'load_coef']

class UserVPNSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVPN
        fields = ['balance', 'is_blocked']






class UserRegistrationSerializer(serializers.ModelSerializer):
    device_type = serializers.CharField()
    device_id = serializers.CharField()
    class Meta:
        model = UserVPN
        fields = ('email', 'password', 'device_type', 'device_id')

    def create(self, validated_data):
        user = UserVPN(
            password= hash_password(validated_data['password']),
            email=validated_data['email'],
            balance = 50.0,
            is_email_verified = False
        )
        user.save()
        device = Device(device_type = validated_data['device_type'], device_id = validated_data['device_id'], user = user)
        device.save()
        tariff = Tariff(name = 'free', descryption = 'Тариф с просмотром рекламы', cost_in_day = 5, max_number_of_devices = 1, max_speed_in_mbps = 5, user = user)
        tariff.save()
        return user

