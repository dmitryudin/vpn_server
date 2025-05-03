




class SubscribeEntity:
    def __init__(self, id=None,  username=None, password=None, last_payment=None, is_active=None, server_id=None, days_at_subscribe=None, user_id=None, device_type=None):
        self.id = id
        self.device_type = device_type
        self.username = username
        self.password = password
        self.is_active = is_active
        self.last_payment = last_payment
        self.days_at_subscribe =  days_at_subscribe
        self.server_id = server_id 
        self.user_id = user_id 