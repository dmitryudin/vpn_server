from django.db import models
from django.contrib import admin

# Create your models here.
class UserVPN(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=200)
    is_email_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    balance = models.FloatField(default=50.0)


class Server(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    ip = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    load_coef = models.FloatField(default=0.0)



class UserVpnAdmin(admin.ModelAdmin):
    list_display = ('email', 'balance', 'is_email_verified')


class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'ip', 'username', 'password', 'country')

admin.site.register(UserVPN, UserVpnAdmin)
admin.site.register(Server, ServerAdmin)