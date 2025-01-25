import telebot;
import threading


def start_bot():
    bot = telebot.TeleBot('7654170202:AAHV1Wlf3fv6iBxk2kq6-qb7M-sVNgfhsiI')


    @bot.message_handler(content_types=['text'])
    def start(message):
        if message.text == '/reg':
            bot.send_message(message.from_user.id, "Как тебя зовут?")
            # bot.register_next_step_handler(message, get_name); #следующий шаг – функция get_name
        else:
            bot.send_message(message.from_user.id, 'Напиши /reg')
    
    bot.polling(none_stop=True, interval=0)
    


t1 = threading.Thread(target=start_bot)
t1.setDaemon(True)
t1.start()
