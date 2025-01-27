import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, sender_password, recipient_email, subject, body):
    # Создаем сообщение
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Добавляем текстовое содержимое
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Устанавливаем соединение с SMTP сервером
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Используем TLS
            server.login(sender_email, sender_password)  # Логинимся
            server.send_message(msg)  # Отправляем сообщение

        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    # Настройки отправителя
    sender_email = 'cryptonvpnone@gmail.com'  # Замените на ваш email
    sender_password = 'unxs htny uggj ghsc'  # Замените на ваш пароль
    recipient_email = 'dmitr.yudin@mail.ru'  # Замените на email получателя
    subject = 'Email Verification'
    body = 'Click the link to verify your email: http://your-domain.com/verify-email'

    send_email(sender_email, sender_password, recipient_email, subject, body)