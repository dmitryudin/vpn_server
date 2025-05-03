


class UserEntity:
    def __init__(self, id=None, telegram_id=None, balance=None, is_blocked=None):
        self.id = id
        self.telegram_id = telegram_id
        self.is_blocked = is_blocked
        self.balance = balance
      