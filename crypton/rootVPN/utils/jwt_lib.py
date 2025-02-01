import jwt
import datetime
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

# Секретный ключ для подписи токенов
SECRET_KEY = settings.SECRET_KEY

# Создание токена
def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365 * 5)  # Время жизни токена
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# Проверка токена
def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token has expired.'
    except jwt.InvalidTokenError:
        return 'Invalid token.'


def jwt_required(func):
    def wrapper(*args, **kwargs):
        print("Что-то происходит до вызова функции. ", *kwargs)
        request = args[1]
        auth = request.META.get('HTTP_AUTHORIZATION')
        if not auth:
            return Response({"error": "Учетные данные не предоставлены"}, status=status.HTTP_401_UNAUTHORIZED)

        # Извлекаем и декодируем учетные данные
        try:
            auth_type, credentials = auth.split(' ')
            if auth_type != 'Token':
                return Response({"error": "Неверный тип аутентификации"}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            return Response({"error": "Неверный тип аутентификации"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user_id = decode_token(credentials)['user_id']
        except:
            return Response({"error": "invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        

        result = func(*args, **kwargs)
        print("Что-то происходит после вызова функции.")
        return result
    return wrapper