from ..entities.subscribe_entity import SubscribeEntity
from ..models import UserVPN, Subscribe
from asgiref.sync import sync_to_async


class SubscribeRepository:



    @sync_to_async
    def create(self, subscribe: SubscribeEntity):
        if not Subscribe.objects.filter(username=subscribe.username).exists():
            subscribe = Subscribe(username=subscribe.username, password=subscribe.password, last_payment=subscribe.last_payment, days_at_subscribe=subscribe.days_at_subscribe, server_id=subscribe.server_id, user_id = subscribe.user_id, device_type=subscribe.device_type)
            subscribe.save()
            
    @sync_to_async
    def update(self, subscribe: SubscribeEntity):
        subscribe_db = Subscribe.objects.filter(username=subscribe.username).first()
        subscribe_db.username = subscribe.username
        subscribe_db.password = subscribe.password
        subscribe_db.last_payment = subscribe.last_payment
        subscribe_db.days_at_subscribe = subscribe.days_at_subscribe
        subscribe_db.server_id = subscribe.server_id
        subscribe_db.user_id = subscribe.user_id
        subscribe_db.device_type = subscribe.device_type
        subscribe_db.save()


    @sync_to_async
    def get_by_user_id(self, user_id, device_type) -> SubscribeEntity:
        subscribe = Subscribe.objects.filter(
            user_id=user_id,
            device_type=device_type  # Added device_type filter
        ).first()
        
        if subscribe:
            return SubscribeEntity(
                device_type=subscribe.device_type,
                last_payment=subscribe.last_payment,
                days_at_subscribe=subscribe.days_at_subscribe,
                username=subscribe.username,
                password=subscribe.password,
                server_id=subscribe.server_id,
                user_id=subscribe.user_id
            )
        return None

    @sync_to_async
    def get(self, username)->SubscribeEntity:
        subscribe = Subscribe.objects.filter(username=username).first()
        return SubscribeEntity(username=subscribe.username, password=subscribe.password, last_payment=subscribe.last_payment, days_at_subscribe=subscribe.days_at_subscribe, server_id=subscribe.server_id, user_id = subscribe.user_id, device_type=subscribe.device_type)

    @sync_to_async
    def delete(self, username):
        subscribe_db = Subscribe.objects.filter(username=username).first()
        subscribe_db.delete()
