import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Установите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypton.settings')

app = Celery('crypton')

# Настройка из файла settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск задач во всех приложениях
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")



app.conf.beat_schedule = {
# create an object for your scheduling your task
    'process_daily_subscription_charges': {
        'task': 'rootVPN.tasks.process_daily_subscription_charges', #app_name.tasks.function_name
        'schedule': 3600.0*12, #crontab() means run every minute
        # 'args' : (..., ...) In case function takes parameters, add them here
    },
     'sync_users': {
        'task': 'rootVPN.tasks.update_subscription', #app_name.tasks.function_name
        'schedule': 3600.0, #crontab() means run every minute
        # 'args' : (..., ...) In case function takes parameters, add them here
    },


}