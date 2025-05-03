import asyncio
import sqlite3
import uuid
import secrets
import hashlib


from datetime import datetime, timedelta
from typing import Optional
from ..domain.domain import create_subscription
from ..domain.ios_config import generate_ios_config

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import os

from ..repositories.user_repository import UserRepository
from ..repositories.subscribe_repository import SubscribeRepository
from ..repositories.server_repository import ServerRepository
from ..entities.user_entity import UserEntity

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TINKOFF_TERMINAL_KEY = os.getenv("TINKOFF_TERMINAL_KEY")
TINKOFF_PASSWORD = os.getenv("TINKOFF_PASSWORD")
TINKOFF_API_URL = "https://securepay.tinkoff.ru/v2/Init"
TINKOFF_CHECK_URL = "https://securepay.tinkoff.ru/v2/GetState"

# Инициализация бота
bot = Bot(token=TELEGRAM_TOKEN)
print('bot is initialized')
dp = Dispatcher()



# Состояния для FSM
class SubscriptionForm(StatesGroup):
    SELECT_SUBSCRIPTION = State()
    AWAITING_PAYMENT = State()
    INSTRUCTIONS = State()

# Генерация учетных данных VPN
def generate_vpn_credentials():
    user = f"user_{uuid.uuid4().hex[:8]}"
    password = secrets.token_hex(8)
    return user, password

# Создание подписи для Тинькофф API
def generate_tinkoff_token(data: dict) -> str:
    data = data.copy()
    data["Password"] = TINKOFF_PASSWORD
    sorted_data = {k: str(v) for k, v in sorted(data.items()) if k not in ["Receipt", "DATA"]}
    concat = "".join(sorted_data.values())
    return hashlib.sha256(concat.encode()).hexdigest()

# Создание платежа через Тинькофф
def create_tinkoff_payment(telegram_id: int, amount: int, order_id: str) -> Optional[dict]:
    payload = {
        "TerminalKey": TINKOFF_TERMINAL_KEY,
        "Amount": amount * 100,  # В копейках
        "OrderId": order_id,
        "Description": f"VPN Subscription for Telegram ID {telegram_id}",
        "NotificationURL": "https://your-domain.com/tinkoff-webhook",  # Замените на ваш URL
        "SuccessURL": "https://your-domain.com/success",
        "FailURL": "https://your-domain.com/fail",
        "DATA": {"TelegramID": str(telegram_id)},
    }
    payload["Token"] = generate_tinkoff_token(payload)
    
    response = requests.post(TINKOFF_API_URL, json=payload)
    if response.status_code == 200:
        return response.json()
    return None

# Проверка статуса платежа
def check_tinkoff_payment(payment_id: str) -> str:
    payload = {
        "TerminalKey": TINKOFF_TERMINAL_KEY,
        "PaymentId": payment_id,
    }
    payload["Token"] = generate_tinkoff_token(payload)
    
    response = requests.post(TINKOFF_CHECK_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("Status", "PENDING")
    return "ERROR"

# Сохранение пользователя и подписки
def save_user_subscription(telegram_id: int, username: str, subscription_type: str, payment_id: str):
    conn = sqlite3.connect("vpn_subscriptions.db")
    cursor = conn.cursor()
    
    # Генерация учетных данных
    user_vpn, password_vpn = generate_vpn_credentials()
    
    # Сохранение пользователя
    cursor.execute(
        "INSERT OR REPLACE INTO users (telegram_id, username, user_vpn, password_vpn) VALUES (?, ?, ?, ?)",
        (telegram_id, username, user_vpn, password_vpn)
    )
    
    # Вычисление дат подписки
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30 if subscription_type == "monthly" else 365)
    
    # Сохранение подписки
    cursor.execute(
        """
        INSERT INTO subscriptions (telegram_id, subscription_type, start_date, end_date, payment_id, payment_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (telegram_id, subscription_type, start_date.isoformat(), end_date.isoformat(), payment_id, "PENDING")
    )
    
    conn.commit()
    conn.close()
    return user_vpn, password_vpn, end_date

# Обновление статуса подписки
def update_subscription_status(payment_id: str, status: str):
    conn = sqlite3.connect("vpn_subscriptions.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE subscriptions SET payment_status = ? WHERE payment_id = ?",
        (status, payment_id)
    )
    conn.commit()
    conn.close()

# Получение информации о подписке
def get_subscription_info(telegram_id: int):
    conn = sqlite3.connect("vpn_subscriptions.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.subscription_type, s.end_date, u.user_vpn, u.password_vpn
        FROM subscriptions s
        JOIN users u ON s.telegram_id = u.telegram_id
        WHERE s.telegram_id = ? AND s.payment_status = 'CONFIRMED'
        ORDER BY s.end_date DESC
        LIMIT 1
        """,
        (telegram_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result

# Главное меню с эмодзи
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Купить подписку 🛒")],
            [KeyboardButton(text="Инструкции по настройке 📚")],
            [KeyboardButton(text="Моя подписка 📋")],
            [KeyboardButton(text="Поддержка 💬")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Команда /start с приветственным сообщением
@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    telegram_id = message.from_user.username
    print(telegram_id)
    await UserRepository().create(UserEntity(telegram_id=user_id))
    await message.answer(
        "Добро пожаловать в VPN-бот! 😊\n"
        "Выберите действие:",
        reply_markup=get_main_menu()
    )

    await state.clear()

# Обработка текстовых сообщений для меню
@dp.message(lambda message: message.text in ["Купить подписку 🛒", "Инструкции по настройке 📚", "Моя подписка 📋", "Поддержка 💬"])
async def handle_menu(message: types.Message, state: FSMContext):
    if message.text == "Купить подписку 🛒":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Месячная подписка (120 руб) ⏰", callback_data="monthly")],
            # [InlineKeyboardButton(text="Годовая подписка (5000 руб) 📅", callback_data="yearly")],
        ])
        await message.answer(
            "Выберите тип подписки на VPN:",
            reply_markup=keyboard
        )
        await state.set_state(SubscriptionForm.SELECT_SUBSCRIPTION)
    elif message.text == "Инструкции по настройке 📚":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="iOS (iPhone/iPad) 🍏", callback_data="instructions_ios")],
            [InlineKeyboardButton(text="Android 🤖", callback_data="instructions_android")],
            [InlineKeyboardButton(text="macOS 🖥️", callback_data="instructions_macos")],
            [InlineKeyboardButton(text="Windows 💻", callback_data="instructions_windows")],
        ])
        await message.answer(
            "Выберите вашу платформу для получения инструкций:",
            reply_markup=keyboard
        )
        await state.set_state(SubscriptionForm.INSTRUCTIONS)
    elif message.text == "Моя подписка 📋":
        telegram_id = message.from_user.id
        subscribe = await SubscribeRepository().get_by_telegram_id(telegram_id=telegram_id)
        
        
        if subscribe:
            server = await ServerRepository().get(subscribe.server_id)
            
            await message.answer(
                f"Ваша подписка: {subscribe.device_type}\n"
                f"Осталось {subscribe.days_at_subscribe} дней\n"
                f"Скачать профиль VPN: http://147.45.249.29:8000/download-vpn/?username={subscribe.username}&password={subscribe.password}&url={server.url}&redirect=safari\n"
            )
        else:
            await message.answer("У вас нет активной подписки.")
    elif message.text == "Поддержка 💬":
        await message.answer(
            "Для поддержки напишите @your_support_username или в чат: https://t.me/your_support_chat\n"
            "Мы всегда рады помочь! 😊"
        )

# Обработка выбора подписки
@dp.callback_query(StateFilter(SubscriptionForm.SELECT_SUBSCRIPTION))
async def process_subscription_type(callback: types.CallbackQuery, state: FSMContext):
    try:
        if callback.data not in ["monthly", "yearly"]:
            await callback.answer("Invalid choice")
            return
        
        subscription_type = callback.data
        telegram_id = callback.from_user.id
        print('Processing subscription request...')
        
        
        # Очищаем состояние
        await state.clear()
        
        # Получаем данные подписки
        try:
            url, username, password = await create_subscription(30, telegram_id, device_type='iphone')
            
            # # Генерируем конфиг
            # config_content = generate_ios_config(
            #     username=username,
            #     password=password,
            #     server_url=url
            # )
            
            # Отправляем сообщение с инструкциями
            await callback.message.answer(
                f"Платеж подтвержден! ✅\n\n"
                f"Открывать ссылку только в Safari!!! \n\n"
                f"Скачать профиль VPN: http://147.45.249.29:8000/download-vpn/?username={username}&password={password}&url={url}&redirect=safari\n"
                f"Как активироват профиль смотри в меню"
            )

        except Exception as e:
            print(e)
            await callback.answer(f'Ошибка {e}')
        
        
        # Обязательно отвечаем на callback
        await callback.answer()
        
        # # Очищаем состояние
        # await state.clear()
        
    except Exception as e:
        print(f"Error in process_subscription_type: {e}")
        await callback.answer(f"An error occurred, please try again {e}")
        await state.clear()
    
    # Создание платежа
    # payment_data = create_tinkoff_payment(callback.from_user.id, amount, order_id)
    
    # if payment_data and payment_data.get("Success"):
    #     payment_id = payment_data["PaymentId"]
    #     payment_url = payment_data["PaymentURL"]
        
    #     # Сохранение данных подписки
    #     user_vpn, password_vpn, end_date = save_user_subscription(
    #         callback.from_user.id, callback.from_user.username or "unknown", subscription_type, payment_id
    #     )
        
    #     # Отправка ссылки на оплату
    #     keyboard = InlineKeyboardMarkup(inline_keyboard=[
    #         [InlineKeyboardButton(text="Оплатить", url=payment_url)],
    #         [InlineKeyboardButton(text="Проверить оплату", callback_data=f"check_{payment_id}")]
    #     ])
    #     await callback.message.answer(
    #         f"Для активации {subscription_type} подписки, пожалуйста, оплатите по ссылке ниже:",
    #         reply_markup=keyboard
    #     )
    #     await state.set_state(SubscriptionForm.AWAITING_PAYMENT)
    # else:
    #     await callback.message.answer("Ошибка при создании платежа. Попробуйте позже.")
    
    # await callback.answer()

# Проверка статуса оплаты
@dp.callback_query(StateFilter(SubscriptionForm.AWAITING_PAYMENT))
async def check_payment_status(callback: types.CallbackQuery, state: FSMContext):
    if not callback.data.startswith("check_"):
        await callback.answer("Неверный запрос.")
        return
    
    payment_id = callback.data.split("_")[1]
    status = check_tinkoff_payment(payment_id)
    
    if status == "CONFIRMED":
        update_subscription_status(payment_id, "CONFIRMED")
        
        # Получение данных пользователя
        conn = sqlite3.connect("vpn_subscriptions.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.user_vpn, u.password_vpn, s.end_date
            FROM users u
            JOIN subscriptions s ON u.telegram_id = s.telegram_id
            WHERE s.payment_id = ?
            """,
            (payment_id,)
        )
        user_vpn, password_vpn, end_date = cursor.fetchone()
        conn.close()
        
        await callback.message.answer(
            f"Оплата подтверждена! ✅\n\n"
            f"Ваши учетные данные для VPN:\n"
            f"Пользователь: {user_vpn}\n"
            f"Пароль: {password_vpn}\n"
            f"Подписка активна до: {end_date}\n\n"
            f"Сохраните эти данные в надежном месте.\n"
            f"Для настройки VPN следуйте инструкциям: выберите 'Инструкции по настройке' в меню."
        )
        await state.clear()
    elif status in ["REJECTED", "CANCELED"]:
        await callback.message.answer("Оплата была отклонена или отменена. Попробуйте снова.")
        await state.clear()
    else:
        await callback.message.answer("Оплата еще не подтверждена. Попробуйте проверить позже.")
    
    await callback.answer()

# Обработка выбора инструкций с фото
@dp.callback_query(StateFilter(SubscriptionForm.INSTRUCTIONS))
async def send_instructions(callback: types.CallbackQuery, state: FSMContext):
    try:
        if callback.data == "instructions_ios":
            # Временный URL для тестирования; замените на ваш реальный URL
            photo = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
            caption = (
                "Инструкция по настройке VPN на iOS (iPhone/iPad):\n\n"
                "1. Откройте **Настройки**.\n"
                "2. Перейдите в **Общие** → **VPN**.\n"
                "3. Нажмите **Добавить конфигурацию VPN**.\n"
                "4. Выберите тип **IKEv2** (или другой, если ваш VPN использует другой протокол).\n"
                "5. Введите следующие данные:\n"
                "   - **Описание**: Название вашего VPN (например, 'Мой VPN').\n"
                "   - **Сервер**: IP-адрес вашего VPN-сервера (например, `192.168.1.100`).\n"
                "   - **Удаленный ID**: Обычно совпадает с IP-адресом сервера.\n"
                "   - **Локальный ID**: Оставьте пустым или введите, если требуется.\n"
                "   - **Аутентификация**: Введите ваш `user` и `password`, полученные от бота.\n"
                "6. Нажмите **Готово**.\n"
                "7. Включите VPN, переключив переключатель рядом с названием вашей конфигурации.\n\n"
                "Если у вас есть вопросы, напишите в поддержку 💬"
            )
            await bot.send_photo(chat_id=callback.message.chat.id, photo=photo, caption=caption)
        elif callback.data == "instructions_android":
            # Временный URL для тестирования; замените на ваш реальный URL
            photo = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
            caption = (
                "Инструкция по настройке VPN на Android:\n\n"
                "1. Откройте **Настройки**.\n"
                "2. Перейдите в **Сеть и интернет** → **VPN**.\n"
                "3. Нажмите **Добавить VPN** или **+**.\n"
                "4. Введите следующие данные:\n"
                "   - **Имя**: Название вашего VPN (например, 'Мой VPN').\n"
                "   - **Тип**: Выберите **L2TP/IPSec PSK** (или другой, если ваш VPN использует другой протокол).\n"
                "   - **Адрес сервера**: IP-адрес вашего VPN-сервера (например, `192.168.1.100`).\n"
                "   - **Предустановленный ключ IPSec**: Введите ключ, если он требуется (уточните у администратора VPN).\n"
                "   - **Имя пользователя** и **Пароль**: Введите ваш `user` и `password`, полученные от бота.\n"
                "5. Нажмите **Сохранить**.\n"
                "6. Подключитесь, нажав на название вашей VPN-конфигурации.\n\n"
                "Если у вас есть вопросы, напишите в поддержку 💬"
            )
            await bot.send_photo(chat_id=callback.message.chat.id, photo=photo, caption=caption)
        elif callback.data == "instructions_macos":
            # Временный URL для тестирования; замените на ваш реальный URL
            photo = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
            caption = (
                "Инструкция по настройке VPN на macOS:\n\n"
                "1. Откройте **Системные настройки** (или **Системные предпочтения** в старых версиях).\n"
                "2. Перейдите в раздел **Сеть**.\n"
                "3. Нажмите **+** в нижнем левом углу, чтобы добавить новое подключение.\n"
                "4. В выпадающем меню **Интерфейс** выберите **VPN**.\n"
                "5. Установите **Тип VPN** в **IKEv2** (или другой, если ваш VPN использует другой протокол).\n"
                "6. Введите название подключения, например, 'Мой VPN', и нажмите **Создать**.\n"
                "7. Заполните поля:\n"
                "   - **Адрес сервера**: IP-адрес вашего VPN-сервера (например, `192.168.1.100`).\n"
                "   - **Удаленный ID**: Обычно совпадает с IP-адресом сервера.\n"
                "   - **Локальный ID**: Оставьте пустым или введите, если требуется.\n"
                "8. Нажмите **Настройки аутентификации** и выберите **Имя пользователя**.\n"
                "   - Введите ваш `user` и `password`, полученные от бота.\n"
                "9. Нажмите **ОК**, затем **Применить**.\n"
                "10. Нажмите **Подключиться**, чтобы активировать VPN.\n\n"
                "Если у вас есть вопросы, напишите в поддержку 💬"
            )
            await bot.send_photo(chat_id=callback.message.chat.id, photo=photo, caption=caption)
        elif callback.data == "instructions_windows":
            # Временный URL для тестирования; замените на ваш реальный URL
            photo = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
            caption = (
                "Инструкция по настройке VPN на Windows:\n\n"
                "1. Откройте **Параметры** (нажмите Win + I).\n"
                "2. Перейдите в **Сеть и Интернет** → **VPN**.\n"
                "3. Нажмите **Добавить VPN-подключение**.\n"
                "4. Заполните поля:\n"
                "   - **Поставщик VPN**: Выберите **Windows (встроенный)**.\n"
                "   - **Имя подключения**: Название вашего VPN (например, 'Мой VPN').\n"
                "   - **Имя или адрес сервера**: IP-адрес вашего VPN-сервера (например, `192.168.1.100`).\n"
                "   - **Тип VPN**: Выберите **L2TP/IPSec с предварительным ключом** (или другой, если требуется).\n"
                "   - **Предварительный ключ**: Введите ключ, если он требуется (уточните у администратора VPN).\n"
                "   - **Тип данных для входа**: Выберите **Имя пользователя и пароль**.\n"
                "   - Введите ваш `user` и `password`, полученные от бота.\n"
                "5. Нажмите **Сохранить**.\n"
                "6. Вернитесь в раздел **VPN**, выберите созданное подключение и нажмите **Подключиться**.\n"
                "7. Введите имя пользователя и пароль еще раз, если потребуется, и нажмите **ОК**.\n\n"
                "Если у вас есть вопросы, напишите в поддержку 💬"
            )
            await bot.send_photo(chat_id=callback.message.chat.id, photo=photo, caption=caption)
        else:
            await callback.answer("Неверный выбор.")
    except Exception as e:
        await callback.message.answer(
            f"Ошибка при отправке изображения: {str(e)}. Пожалуйста, попробуйте позже или обратитесь в поддержку 💬."
        )
    
    await state.clear()
    await callback.answer()

# Запуск бота
async def bot_main():
    await dp.start_polling(bot)

def run_bot():
    loop = asyncio.new_event_loop()
    
    # Отключаем обработку сигналов
    def noop(*args, **kwargs): pass
    loop.add_signal_handler = noop
    
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(dp.start_polling(bot))
    finally:
        
        print('bot stopped')
        loop.close()

# import fcntl
# import atexit

# def unlock_file():
#     if hasattr(unlock_file, 'lock_file'):
#         fcntl.flock(unlock_file.lock_file, fcntl.LOCK_UN)
#         unlock_file.lock_file.close()

# try:
#     lock_file = open('bot.lock', 'w')
#     unlock_file.lock_file = lock_file  # Сохраняем ссылку для atexit
#     fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
#     atexit.register(unlock_file)  # Разблокировать при выходе
# except IOError:
#     print("error shutdown")
#     exit(1)
# except Exception as e:
#     print(f"error block {e}")
#     exit(1)

# print("locked")

