from uuid import uuid4
import time
from confluent_kafka import Consumer, Producer, admin
import json

from enum import Enum

class VPNUserManagerStatus(Enum):
    CONFLICT = 0
    USER_NOT_FOUND = 1
    SERVER_NOT_RESPONCE=2
    INVALID_CONFIG_FILE = 3
    INVALID_ACTION= 4
    UNEXPECTED_ERROR = 5
    SUCCESS = 6

class VPNUserManager:
    def __init__(self, kafka_config=None):
        # Базовый конфиг для всех компонентов
        base_config = kafka_config or {'bootstrap.servers': '0.0.0.0:9092'}
        
        # Конфигурация для Consumer'ов
        self.consumer_config = {
            **base_config,
            'group.id': 'vpn-user-manager',
            'auto.offset.reset': 'earliest'
        }
        
        # Конфигурация для Producer'ов
        self.producer_config = base_config
        
        # Конфигурация для AdminClient
        self.admin_client = admin.AdminClient(base_config)

    def _create_topic(self, topic_name):
        """Create temporary topic in Kafka"""
        new_topic = admin.NewTopic(topic_name, num_partitions=1, replication_factor=1)
        try:
            fs = self.admin_client.create_topics([new_topic])
            fs[topic_name].result()
            print(f"Topic {topic_name} created successfully")
            return True
        except Exception as e:
            print(f"Error creating topic {topic_name}: {e}")
            return False

    def _delete_topic(self, topic_name):
        """Delete temporary topic"""
        try:
            fs = self.admin_client.delete_topics([topic_name])
            fs[topic_name].result()
            print(f"Topic {topic_name} deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting topic {topic_name}: {e}")
            return False

    def _send_kafka_event(self, topic: str, data: dict):
        """Universal method for sending messages"""
        producer = Producer(self.producer_config)  # Используем правильный конфиг
        try:
            producer.produce(
                topic=topic,
                value=json.dumps(data).encode('utf-8'),
                callback=lambda err, _: print(f"Delivery failed: {err}") if err else None
            )
            producer.flush()
        except Exception as e:
            print(f"Failed to send message to {topic}: {e}")
        finally:
            producer.poll(0)

    def send_vpn_command(self, topic: str, action: str, username: str, password: str = None, timeout: float = 5.0)->VPNUserManagerStatus:
        """Send command through temporary topic"""
        correlation_id = str(uuid4())
        reply_topic = f"vpn-reply-{correlation_id}"
        
        if not self._create_topic(reply_topic):
            raise Exception("Failed to create temporary reply topic")

        try:
            # Создаем Consumer с правильным конфигом
            reply_consumer = Consumer({
                'bootstrap.servers': self.consumer_config['bootstrap.servers'],
                'group.id': f"vpn-reply-group-{correlation_id}",
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False
            })
            reply_consumer.subscribe([reply_topic])

            command = {
                'action': action,
                'username': username,
                'password': password,
                'reply_to': reply_topic,
                'correlation_id': correlation_id,
                'timestamp': int(time.time() * 1000)
            }
            self._send_kafka_event(topic, command)

            start_time = time.time()
            while time.time() - start_time < timeout:
                msg = reply_consumer.poll(1.0)
                if msg:
                    print(msg.value())
                    try:
                        response = json.loads(msg.value())
                        if response.get('correlation_id') == correlation_id:
                            if (response['status'] == 'success'): return VPNUserManagerStatus.SUCCESS
                            if (response['status'] == 'failed'):
                                if (response['error']=='conflict'): return VPNUserManagerStatus.CONFLICT
                                if (response['error']=='invalid_config_file'): return VPNUserManagerStatus.INVALID_CONFIG_FILE
                                if (response['error']=='not_found'): return VPNUserManagerStatus.USER_NOT_FOUND
                                if (response['error']=='invalid_action'): return VPNUserManagerStatus.INVALID_ACTION
                               
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        continue

            return VPNUserManagerStatus.SERVER_NOT_RESPONCE
        finally:
            reply_consumer.close()
            self._delete_topic(reply_topic)