from threading import Thread
from django.apps import AppConfig
from django.apps import AppConfig
from django.conf import settings
import time

from .utils.telegram_bot import run_bot



class RootvpnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rootVPN'
    _initialized = False  # Классовый атрибут для отслеживания состояния

    def ready(self):
        if self.__class__._initialized:
            return
        
        from .network_monitor import KafkaConsumerThread

        self.__class__._initialized = True
        print("Application initialization complete")
        
        

        # bot_thread = Thread(target=run_bot)
        # bot_thread.start()

        # Запускаем поток потребителя
        
