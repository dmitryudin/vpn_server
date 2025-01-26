from django.core.mail import send_mail
from django.shortcuts import render
from django.http import JsonResponse
from .models import UserVPN  # Предполагаем, что у вас есть модель UserVPN
from .utils import generate_verification_token  # Импортируйте функцию генерации токена


def send_verification_email(user_id):
    try:
        user = UserVPN.objects.get(id=user_id)
        token = generate_verification_token(user.email)
        verification_link = f"http://your-domain.com/verify-email/?token={token}"

        send_mail(
            'Email Verification',
            f'Click the link to verify your email: {verification_link}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return {'message': 'Verification email sent!'}
    except UserVPN.DoesNotExist:
        return {'error': 'User not found'}

from django.core.signing import BadSignature

def verify_email(request):
    token = request.GET.get('token')
    signer = Signer()

    try:
        email = signer.unsign(token)
        user = UserVPN.objects.get(email=email)
        user.is_verified = True  # Предполагаем, что у вас есть поле is_verified в модели
        user.save()
        return JsonResponse({'message': 'Email verified successfully!'})
    except BadSignature:
        return JsonResponse({'error': 'Invalid token'}, status=400)
    except UserVPN.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)