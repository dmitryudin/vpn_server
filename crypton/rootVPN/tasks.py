from celery import shared_task
from django.utils import timezone
import asyncio
from .vpn_service.user_vpn_rest_manager import VPNUserRestManager
from .models import Subscribe, UserVPN, Server
from datetime import timedelta, datetime
import logging

from asgiref.sync import async_to_sync
logger = logging.getLogger(__name__)




# @shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
@shared_task
def update_subscription():
    """Задача для синхронизации пользователей на VPN-серверах"""
    logger.info("Starting servers synchronization")
    
    try:
        # 1. Получаем список всех серверов
        servers = Server.objects.all()
        
        for server in servers:
            try:
                # 2. Получаем активные подписки для текущего сервера
                active_subscriptions = Subscribe.objects.filter(
                    server=server,
                    days_at_subscribe__gt=0
                ).exclude(username__isnull=True).exclude(username='')
                
                # 3. Формируем список username
                active_usernames = list(
                    active_subscriptions.values_list('username', flat=True)
                )
                
                logger.info(f"Found {len(active_usernames)} active users for {server.url}")
                base_url=f'http://{server.ip}:8080'
                logger.info(f"Base url is  {base_url}")
                if not active_usernames:
                    continue
                
                # 4. Отправляем на сервер VPN
                vpn_manager =  VPNUserRestManager(
                    base_url=f'http://{server.ip}:8080',
                    # Предполагаем, что сервер использует стандартные учетные данные
                    username='admin',
                    password='securepassword')
                try: 
                    result = asyncio.run(vpn_manager.sync_users(active_usernames))
                    logger.info(f" result = {result}")
                except:
                    pass
            
                
                # if result.success:
                #     logger.info(f"Successfully synced {len(active_usernames)} users for {server.url}")
                # else:
                #     logger.error(f"Sync failed for {server.name}: {result.message}")
                        
            except Exception as e:
                logger.error(f"Error processing server {server.url}: {str(e)}")
                continue
                

        logger.info("Servers synchronization completed")
        return {"status": "success", "processed_servers": servers.count()}
    
    except Exception as e:
        logger.error(f"Critical error in server sync: {str(e)}")
        # self.retry(exc=e, countdown=60)


@shared_task
def process_daily_subscription_charges():

    today = timezone.now().date()
    logger.info(f"Starting daily subscription processing for {today}")
    
    # Получаем подписки, у которых последнее списание было не сегодня
    subscriptions_to_process = Subscribe.objects.filter(
        last_payment__date__lt=today,  # Списание еще не проводилось сегодня
        user__is_blocked=False,
        days_at_subscribe__gt=0  # Только активные подписки
    ).select_related('user')
    
    for subscription in subscriptions_to_process:
        try:
            user = subscription.user
            days_passed = (today - subscription.last_payment.date()).days
            
            # Проверяем, что с последнего списания прошел хотя бы 1 день
            if days_passed < 1:
                continue
                

            subscription.days_at_subscribe -= days_passed
            subscription.last_payment = timezone.now()  # Обновляем дату последнего списания
            
            if subscription.days_at_subscribe <= 0:
                subscription.days_at_subscribe = 0
                logger.info(f"Subscription {subscription.id} expired")
            
            subscription.save()

  
                
        except Exception as e:
            logger.error(f"Error processing subscription {subscription.id}: {str(e)}")
            continue

    logger.info("Daily subscription processing completed")
    return "Done"