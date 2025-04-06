from threading import Thread
from django.apps import AppConfig
from django.apps import AppConfig

import time

from .utils.telegram_bot import run_bot


class RootvpnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rootVPN'

    def ready(self):
        from .network_monitor import KafkaConsumerThread
        from django.conf import settings

        # bot_thread = Thread(target=run_bot)
        # bot_thread.start()

        # Запускаем поток потребителя
        while(True):
            # break
            try:
                consumer_thread = KafkaConsumerThread(settings.KAFKA_TOPIC)
                consumer_thread.start()
                break
            except:
                print('ettemt to attach')
                time.sleep(2)
