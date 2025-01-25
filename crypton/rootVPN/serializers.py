from rest_framework import serializers
from .models import UserVPN, Server
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
    class Meta:
        model = UserVPN
        fields = ('email', 'password')

    def create(self, validated_data):
        user = UserVPN(
            password= hash_password(validated_data['password']),
            email=validated_data['email'],
            balance = 50.0,
            is_email_verified = False
        )

        user.save()
        return user