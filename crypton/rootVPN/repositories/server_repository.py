



from ..models import Server
from django.db.models import Count, Min
from asgiref.sync import sync_to_async

class ServerRepository:
    @sync_to_async
    def get_server_with_min_users(self):
        # Get server with minimum active subscriptions
        return Server.objects.annotate(
            subscription_count=Count('subscribe')  # Changed from 'user' to 'subscribe'
        ).order_by('subscription_count', 'load_coef').first()
#     def __init__(self, dataModel: Server):
#         self.dataModel = dataModel

     
#     def create(: Server):
#         print('created_user')

    
#     def update(user: User):
#         pass

    @sync_to_async
    def get(self, id):
        
        return Server.objects.get(id=id)

    
#     def delete(telegram_id):
#         pass