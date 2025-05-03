from django.db import models
from django.contrib import admin




class Server(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    ip = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    load_coef = models.FloatField(default=0.0)
    max_speed_in_mbps = models.FloatField(default=200.0)
    active_users = models.IntegerField(default=0, null=True)
    api_username = models.CharField(max_length=100, default='admin')
    api_password = models.CharField(max_length=100, default='securepassword')
    last_sync = models.DateTimeField(null=True, blank=True)


# Create your models here.
class UserVPN(models.Model):
    id = models.IntegerField(primary_key=True)
    telegram_id = models.CharField(max_length=100, unique=True, null=True, db_index=True)
    balance = models.FloatField(null=True)
    is_blocked = models.BooleanField(null=True)



class Subscribe(models.Model):
    device_type = username = models.CharField(max_length=100, null=True)
    last_payment = models.DateTimeField(null=True)
    days_at_subscribe =  models.IntegerField(null=True)
    username = models.CharField(max_length=100, unique=True, null=True, db_index=True)
    password = models.CharField(max_length=200, null=True)
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='subscribe', null=True)
    user  = models.ForeignKey(UserVPN, on_delete=models.CASCADE, related_name='subscribe', null=True)


