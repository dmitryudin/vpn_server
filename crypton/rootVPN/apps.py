from django.apps import AppConfig
from django.apps import AppConfig




class RootvpnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rootVPN'

    def ready(self):
        from .network_monitor import KafkaConsumerThread
        from django.conf import settings

        # Запускаем поток потребителя
        consumer_thread = KafkaConsumerThread(settings.KAFKA_TOPIC)
        consumer_thread.start()
