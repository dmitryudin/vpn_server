import telebot
from telebot import types
from threading import Thread
import random

# Ваш токен
API_TOKEN = '7654170202:AAHV1Wlf3fv6iBxk2kq6-qb7M-sVNgfhsiI'
bot = telebot.TeleBot(API_TOKEN)

user_codes = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите /tariffs, чтобы выбрать тариф.")

@bot.message_handler(commands=['tariffs'])
def tariffs(message):
    keyboard = types.InlineKeyboardMarkup()
    
    # Добавляем каждую кнопку в отдельный ряд
    button1 = types.InlineKeyboardButton("Тариф 1 - $10", callback_data='tariff_1')
    button2 = types.InlineKeyboardButton("Тариф 2 - $20", callback_data='tariff_2')
    button3 = types.InlineKeyboardButton("Тариф 3 - $30", callback_data='tariff_3')
    
    keyboard.add(button1)  # Первая кнопка
    keyboard.add(button2)  # Вторая кнопка
    keyboard.add(button3)  # Третья кнопка
    
    bot.send_message(message.chat.id, 'Выберите тариф:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    tariff = call.data
    # Генерация случайного шестизначного кода
    code = f"CODE-{random.randint(100000, 999999)}"
    user_codes[call.from_user.id] = code
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=f"Вы выбрали {tariff}. Ваш код: {code}", chat_id=call.message.chat.id, message_id=call.message.message_id)

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    bot_thread = Thread(target=run_bot)
    bot_thread.start()