from ..entities.user_entity import UserEntity
from ..models import UserVPN
from asgiref.sync import sync_to_async


class UserRepository:
    @sync_to_async
    def create(self, user: UserEntity):
        if not UserVPN.objects.filter(telegram_id=user.telegram_id).exists():
            user = UserVPN(telegram_id=user.telegram_id, balance=user.balance, is_blocked = user.is_blocked)
            user.save()
            
    @sync_to_async
    def update(self, user):
        userVPN = UserVPN.objects.filter(telegram_id=user.telegram_id).first()
        userVPN.balance = user.balance
        userVPN.is_blocked = user.is_blocked
        userVPN.save()


    @sync_to_async
    def get(self, telegram_id)->UserEntity:
        user = UserVPN.objects.get(telegram_id=telegram_id)
        return UserEntity(id=user.id, telegram_id=user.telegram_id, balance=user.balance, is_blocked = user.is_blocked)

    @sync_to_async
    def delete(self, telegram_id):
        user = UserVPN.objects.first(telegram_id=telegram_id)
        user.delete()


 