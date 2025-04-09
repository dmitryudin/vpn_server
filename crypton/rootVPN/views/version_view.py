
from rest_framework.response import Response
from rest_framework import generics

from ..models  import Version

class AndroidVersionView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]  # Защита контроллера
    # authentication_classes = [JWTAuthentication]  # Аутентификация с помощью JWT
    
    def get(self, request):
        version = Version.objects.get(platform='android')
        return Response({
            'availible_version': version.version,
            'url_for_update': version.url,
            
        })
    


class IosVersionView(generics.GenericAPIView):
    def get(self, request):
        version = Version.objects.get(platform='ios')
        return Response({
            'availible_version': version.version,
            'url_for_update': version.url,
            
        })