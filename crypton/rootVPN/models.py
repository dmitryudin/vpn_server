from django.db import models
from django.contrib import admin


class Tariff(models.Model):
    name = models.CharField(max_length=100)
    descryption = models.CharField(max_length=300)
    days = models.FloatField(default=0.0)
    cost = models.FloatField(default=0.0)
    max_number_of_devices = models.IntegerField(default=1)
    max_speed_in_mbps = models.FloatField(default=0.0)

# Create your models here.
class UserVPN(models.Model):
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=200)
    is_email_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    balance = models.FloatField(default=0.0)
    last_payment = models.DateTimeField(null=True)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL,  related_name='tariff', null=True)


class Server(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    ip = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    load_coef = models.FloatField(default=0.0)
    max_speed_in_mbps = models.FloatField(default=200.0)
    active_users = models.IntegerField(default=0, null=True)


class InviteCode(models.Model):
    code = models.CharField(max_length=100)
    balance = models.FloatField(default=50.0)
    user = models.ForeignKey(UserVPN, on_delete=models.CASCADE, related_name='invitations')

class Promocode(models.Model):
    name = models.CharField(max_length=100)
    descryption = models.CharField(max_length=300)
    balance = models.FloatField(default=0.0)



    


class Device(models.Model):
    device_type = models.CharField(max_length=100)
    device_id = models.CharField(max_length=300)
    user = models.ForeignKey(UserVPN, on_delete=models.CASCADE, related_name='devices')

class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'balance', 'user')

class UserVpnAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'balance', 'is_email_verified')


class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'ip', 'username', 'password', 'country', 'max_speed_in_mbps', 'active_users')

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_type', 'device_id', 'user')

class TariffAdmin(admin.ModelAdmin):


    list_display = ('name', 'descryption', 'days', 'cost', 'max_number_of_devices', 'max_speed_in_mbps')

admin.site.register(UserVPN, UserVpnAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(InviteCode, InviteCodeAdmin)