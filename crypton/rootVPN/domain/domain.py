






from ..entities.user_entity import UserEntity
from ..entities.subscribe_entity import SubscribeEntity
from ..models import UserVPN
from ..repositories.user_repository import UserRepository
from ..repositories.server_repository import ServerRepository
from ..repositories.subscribe_repository import SubscribeRepository
from ..vpn_service.user_vpn_rest_manager import *
import uuid
import secrets
import datetime


# Генерация учетных данных VPN
def generate_vpn_credentials():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = secrets.token_hex(8)
    return user, password



async def create_subscription(days, telegram_id, device_type):
    userRepository = UserRepository()
    serverRepositiry = ServerRepository()
    vpnUserManager = VPNUserRestManager() 
    subscribeRepository = SubscribeRepository()
    
    await userRepository.create(UserEntity(telegram_id=telegram_id))
    
    userVPN = await userRepository.get(telegram_id)
    server = await serverRepositiry.get_server_with_min_users()
    username, password = generate_vpn_credentials()
    
    serverUrl = server.url
    serverIp = server.ip
    if server:
        subscription = await subscribeRepository.get_by_user_id(user_id=userVPN.id, device_type=device_type)
        if subscription:
            if not subscription.username:
                subscription.username = username
            if not subscription.password:
                subscription.password = password
            if subscription.server_id:
                serverVPN = await serverRepositiry.get(id=subscription.server_id)
                serverUrl = serverVPN.url
                serverIp = serverVPN.ip
            subscription.is_active = True
            subscription
            subscription.last_payment = datetime.datetime.now()
            subscription.days_at_subscribe = days
            try:
                await vpnUserManager.add_user(username=subscription.username, password=subscription.password)

                await subscribeRepository.update(subscription)
            except Exception as e : raise Exception(str(e)) 
            
        else:
            subscription = SubscribeEntity(username=username, password=password, device_type=device_type, server_id=server.id, user_id=userVPN.id, last_payment=datetime.datetime.now(), days_at_subscribe=days, is_active=True)
            try:
                await vpnUserManager.add_user(username=subscription.username, password=subscription.password)

                await subscribeRepository.create(subscription)
            except Exception as e : raise Exception(str(e)) 

        return serverUrl, subscription.username, subscription.password
        
    else: 
        raise Exception("No server in db")

    


    pass

async def delete_subscribe(username):
    print('delete_subscribe')
    userRepository = UserRepository()
    serverRepositiry = ServerRepository()
    vpnUserManager = VPNUserManager() 
    subscribeRepository = SubscribeRepository()
    subscribe = await subscribeRepository.get(username=username)
    server = await serverRepositiry.ger(subscribe.server_id)
    if (subscribe):
        server = await serverRepositiry.ger(subscribe.server_id)
        vpnUserManager.send_vpn_command(topic=server.ip, action='remove', username=username, password = "",  timeout=8)
        await subscribeRepository.delete(username)