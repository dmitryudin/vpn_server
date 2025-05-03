from uuid import uuid4
import time
import asyncio
from confluent_kafka import Consumer, Producer, admin
import json

class AsyncVPNUserManager:
    def __init__(self, kafka_config=None):
        self.kafka_config = kafka_config or {
            'bootstrap.servers': '0.0.0.0:9092',
            'group.id': 'vpn-user-manager',
            'auto.offset.reset': 'earliest'
        }
        self.admin_client = admin.AdminClient(self.kafka_config)
        self.loop = asyncio.get_event_loop()

    async def _create_topic(self, topic_name):
        """Create temporary topic in Kafka (async)"""
        new_topic = admin.NewTopic(topic_name, num_partitions=1, replication_factor=1)
        try:
            fs = self.admin_client.create_topics([new_topic])
            await self.loop.run_in_executor(None, fs[topic_name].result)
            print(f"Topic {topic_name} created successfully")
            return True
        except Exception as e:
            print(f"Error creating topic {topic_name}: {e}")
            return False

    async def _delete_topic(self, topic_name):
        """Delete temporary topic (async)"""
        try:
            fs = self.admin_client.delete_topics([topic_name])
            await self.loop.run_in_executor(None, fs[topic_name].result)
            print(f"Topic {topic_name} deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting topic {topic_name}: {e}")
            return False

    async def _send_kafka_event(self, topic: str, data: dict):
        """Async method for sending messages"""
        producer = Producer(self.kafka_config)
        try:
            producer.produce(
                topic=topic,
                value=json.dumps(data).encode('utf-8'),
                callback=lambda err, _: print(f"Delivery failed: {err}") if err else None
            )
            await self.loop.run_in_executor(None, producer.flush)
        except Exception as e:
            print(f"Failed to send message to {topic}: {e}")
        finally:
            producer.poll(0)

    async def send_vpn_command(self, topic: str, action: str, username: str, password: str = None, timeout: float = 5.0):
        """Async version of send command with reply handling"""
        correlation_id = str(uuid4())
        reply_topic = f"vpn-reply-{correlation_id}"
        
        if not await self._create_topic(reply_topic):
            raise Exception("Failed to create temporary reply topic")

        consumer = None
        try:
            # Create and configure consumer
            consumer = Consumer({
                'bootstrap.servers': self.kafka_config['bootstrap.servers'],
                'group.id': f"vpn-reply-group-{correlation_id}",
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False
            })
            consumer.subscribe([reply_topic])

            # Create async queue and consumer task
            queue = asyncio.Queue()
            consume_task = self.loop.create_task(self._consume_messages(consumer, queue))

            # Send command
            command = {
                'action': action,
                'username': username,
                'password': password,
                'reply_to': reply_topic,
                'correlation_id': correlation_id,
                'timestamp': int(time.time() * 1000)
            }
            await self._send_kafka_event(topic, command)

            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(self._wait_for_response(queue, correlation_id), timeout)
                return response
            except asyncio.TimeoutError:
                raise TimeoutError("No response received from processing service")

        finally:
            # Cleanup resources
            if consumer:
                consumer.close()
                await self._delete_topic(reply_topic)
            if 'consume_task' in locals():
                consume_task.cancel()

    async def _consume_messages(self, consumer, queue):
        """Background task to consume messages and put them in queue"""
        while True:
            msg = await self.loop.run_in_executor(None, consumer.poll, 0.1)
            if msg is not None:
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                await queue.put(msg)
            await asyncio.sleep(0.01)

    async def _wait_for_response(self, queue, correlation_id):
        """Wait for correct response in queue"""
        while True:
            msg = await queue.get()
            try:
                response = json.loads(msg.value())
                if response.get('correlation_id') == correlation_id:
                    return response['status'] == 'success'
            except Exception as e:
                print(f"Error processing message: {e}")