from django.contrib import admin
from .models import UserVPN, Subscribe, Server
from.repositories.server_repository import ServerRepository
from .vpn_service.user_vpn_manager import VPNUserManager
from .domain.domain import delete_subscribe
from asgiref.sync import async_to_sync

class UserVpnAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'balance', 'is_blocked')


class SubscribeVpnAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password',  'last_payment', 'server', 'user', 'device_type', 'days_at_subscribe')
    def delete_model(self, request, obj):
        print(f"Удаление объекта {obj.id} по запросу пользователя {request.user} {obj.server_id}")
        server = Server.objects.get(id=obj.server_id)
        vpnUserManager = VPNUserManager() 
        vpnUserManager.send_vpn_command(topic=server.ip, action='remove', username=obj.username, password = "",  timeout=8)
        obj.delete()

        
        
        
        
        # super().delete_model(request, obj)

class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'ip',  'country', 'max_speed_in_mbps', 'active_users', 'load_coef')





admin.site.register(UserVPN, UserVpnAdmin)
admin.site.register(Subscribe, SubscribeVpnAdmin)
admin.site.register(Server, ServerAdmin)