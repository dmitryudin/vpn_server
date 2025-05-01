from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from ..models import UserVPN  # Предполагаем, что у вас есть модель UserVPN
from .signer import generate_verification_token  # Импортируйте функцию генерации токена
from django.conf import settings
from django.core.signing import Signer
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def send_verification_email(user_id):
    try:
        user = UserVPN.objects.get(id=user_id)
        token = generate_verification_token(user.email)
        verification_link = f"http://109.73.202.105:8000/api/verify-email/?token={token}"
        

        
                
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header('🔐 Подтверждение сброса пароля | CryptonVPN', 'utf-8')
        msg['From'] = Header('CryptonVPN <support@cryptonvpn.com>', 'utf-8')
        msg['To'] = user.email

        # Текстовая версия для почтовых клиентов без поддержки HTML
        text = f"""Для подтверждения электронной почты перейдите по ссылке:
        {verification_link}

        С уважением, команда CryptonVPN"""

        # HTML-версия письма
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Подтверждение почты</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                }}
                
                body {{
                    background: #f7fafc;
                    padding: 40px 20px;
                }}
                
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem;
                    text-align: center;
                }}
                
                .logo {{
                    width: 160px;
                    height: auto;
                    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
                }}
                
                .content {{
                    padding: 2.5rem;
                    color: #4a5568;
                }}
                
                h1 {{
                    color: #2d3748;
                    margin-bottom: 1.5rem;
                    font-size: 1.875rem;
                }}
                
                .cta-button {{
                    display: inline-block;
                    margin: 2rem 0;
                    padding: 1rem 2rem;
                    background: #4a5568;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 8px;
                    transition: transform 0.2s;
                    font-weight: 600;
                }}
                
                .cta-button:hover {{
                    transform: translateY(-2px);
                    background: #2d3748;
                }}
                
                .footer {{
                    margin-top: 2rem;
                    padding-top: 2rem;
                    border-top: 1px solid #e2e8f0;
                    text-align: center;
                    color: #718096;
                }}
                
                @media (max-width: 640px) {{
                    .content {{
                        padding: 1.5rem;
                    }}
                    
                    h1 {{
                        font-size: 1.5rem;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://i.ibb.co/5KqY0Md/logo-white.png" alt="CryptonVPN" class="logo">
                </div>
                
                <div class="content">
                    <h1>Подтверждение почты</h1>
                    <p>Для завершения регистрации нажмите кнопку ниже:</p>
                    
                    <a href="{verification_link}" class="cta-button">Подтвердить</a>
                    
                    <p>Если вы не регистрировались на сервисе CryptonVPN, проигнорируйте это письмо.</p>
                    
                    <div class="footer">
                        <p>© 2024 CryptonVPN. Все права защищены.</p>
                        <p>Это письмо отправлено автоматически, пожалуйста не отвечайте на него.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Прикрепляем обе версии
        part_text = MIMEText(text, 'plain', 'utf-8')
        part_html = MIMEText(html, 'html', 'utf-8')

        msg.attach(part_text)
        msg.attach(part_html)
        

        try:
            # Устанавливаем соединение с SMTP сервером
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                print('send email begin')
                
                server.starttls()  # Используем TLS
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)  # Логинимся
                server.send_message(msg)  # Отправляем сообщение

            print(f"Email sent successfully to {user.email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

            return {'message': 'Verification email sent!'}
    except UserVPN.DoesNotExist:
        print('user not exist')
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
        return HttpResponse('''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email подтверждён</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        body {
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }

        .confirmation-box {
            background: rgba(255, 255, 255, 0.95);
            padding: 3rem 4rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            text-align: center;
            max-width: 600px;
            width: 100%;
            transform: translateY(20px);
            opacity: 0;
            animation: fadeIn 0.6s ease-out forwards;
        }

        .checkmark {
            width: 80px;
            height: 80px;
            margin: 0 auto 2rem;
            background: #4ade80;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: checkmarkScale 0.4s ease-in-out;
        }

        .checkmark::after {
            content: "✓";
            color: white;
            font-size: 3rem;
            font-weight: bold;
        }

        h1 {
            color: #1a365d;
            font-size: 2.5rem;
            margin-bottom: 1rem;
            line-height: 1.2;
        }

        p {
            color: #4a5568;
            font-size: 1.2rem;
            margin-top: 1rem;
        }

        .button {
            display: inline-block;
            margin-top: 2rem;
            padding: 1rem 2rem;
            background: #4f46e5;
            color: white;
            text-decoration: none;
            border-radius: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        @keyframes fadeIn {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes checkmarkScale {
            0% { transform: scale(0); }
            80% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        @media (max-width: 768px) {
            .confirmation-box {
                padding: 2rem;
            }

            h1 {
                font-size: 2rem;
            }

            .checkmark {
                width: 60px;
                height: 60px;
            }
        }
    </style>
</head>
<body>
    <div class="confirmation-box">
        <div class="checkmark"></div>
        <h1>Ваш e-mail успешно подтвержден!</h1>
        <p>Теперь вы можете пользоваться всеми возможностями сервиса</p>
        <a href="https://yandex.ru" class="button">ОК</a>
    </div>
</body>
</html>
''', content_type="text/html", charset="utf-8")
    except BadSignature:
        return JsonResponse({'error': 'Invalid token'}, status=400)
    except UserVPN.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)