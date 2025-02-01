from django.core.mail import send_mail
from django.shortcuts import render
from django.http import JsonResponse
from ..models import UserVPN  # Предполагаем, что у вас есть модель UserVPN
from .signer import generate_verification_token  # Импортируйте функцию генерации токена
from django.conf import settings
from django.core.signing import Signer
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(user_id):
    try:
        user = UserVPN.objects.get(id=user_id)
        token = generate_verification_token(user.email)
        verification_link = f"http://109.196.101.63:8000/api/verify-email/?token={token}"

        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = user.email
        msg['Subject'] = 'Ссылка для верификации'

        # Добавляем текстовое содержимое
        msg.attach(MIMEText(f'Подтвердите регистрацию CryptonVPN и пользуйтесь Premium бесплатно 10 дней {verification_link}', 'plain'))

        try:
            # Устанавливаем соединение с SMTP сервером
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Используем TLS
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)  # Логинимся
                server.send_message(msg)  # Отправляем сообщение

            print(f"Email sent successfully to {user.email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

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
        user.last_payment = datetime.datetime.now()
        user.balance = user.balance+10
        user.is_email_verified = True  # Предполагаем, что у вас есть поле is_verified в модели
        user.save()
        return JsonResponse({'message': 'Email verified successfully!'})
    except BadSignature:
        return JsonResponse({'error': 'Invalid token'}, status=400)
    except UserVPN.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)