from threading import Thread
from django.apps import AppConfig

import time
import os
import sys

# from .vpn_service.network_monitor import KafkaConsumerThread
# from .telegram_bot.bot import run_bot






from threading import Lock

class RootvpnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rootVPN'
    _initialized = False
    _lock = Lock()  # Блокировка для синхронизации

    def ready(self):
        print(self._initialized)
        
            
        
        from .admin_models import ServerAdmin
        
            

        self._initialized = True
        print("Application initialization complete", sys.argv, 'runserver' in sys.argv)

        if 'runserver' in sys.argv:
            from .vpn_service.network_monitor import KafkaConsumerThread
            from .telegram_bot.bot import run_bot
            from .vpn_service.network_monitor import KafkaConsumerThread
            bot_thread = Thread(target=run_bot)
            bot_thread.start()

        
# lsof -ti :8000 | xargs kill -9
# class RootvpnConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'rootVPN'
#     _initialized = False  # Классовый атрибут для отслеживания состояния

#     def ready(self):
        
#         if self.__class__._initialized:
#             return
        
#         from .vpn_service.network_monitor import KafkaConsumerThread

#         self.__class__._initialized = True
#         print("Application initialization complete")
        
#         # run_bot()
#         if settings.RUN_TELEGRAM_BOT:  # Добавьте эту настройку в settings.py
#             from .telegram_bot.bot import run_bot

#             bot_thread = Thread(target=run_bot)
#             bot_thread.start()
       


#         # Запускаем поток потребителя
        
