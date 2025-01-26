from kafka import KafkaConsumer
import json
import threading
from django.conf import settings
from .models import Server

def get_max_speed(ip_address):
    try:
        # Get the Server object by IP address
        server = Server.objects.get(ip=ip_address)
        max_speed = server.max_speed_in_mbps
        return max_speed
    except Server.DoesNotExist:
        print(f"Server with IP {ip_address} not found.")
        return None

class KafkaConsumerThread(threading.Thread):
    def __init__(self, topic):
        threading.Thread.__init__(self)
        self.topic = topic
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=settings.KAFKA_SERVER,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-group'
        )

    def run(self):
        print(f"Connecting to topic '{self.topic}' on server '{settings.KAFKA_SERVER}'")
        for message in self.consumer:
            data = message.value
            print(f"Received message: {data}")
            # Update or create a record in the Server model
            ip_address = data.get('ip_address')
            speed_sent_mbps = data.get('speed_sent_mbps')
            speed_recv_mbps = data.get('speed_recv_mbps')
            server, created = Server.objects.update_or_create(
                ip=ip_address,
                defaults={
                    'load_coef': float(speed_recv_mbps) / get_max_speed(ip_address)
                }
            )
            if created:
                print(f"Created new server with IP {ip_address}")
            else:
                print(f"Updated data for server with IP {ip_address}")

    def stop(self):
        self.consumer.close()