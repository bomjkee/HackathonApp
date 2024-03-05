import telebot
from telebot import types

token = '7196187930:AAHhF7ABhREJNpOqopRCb94gPRvgUlHewYo'
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item0 = types.KeyboardButton('СДО МИРЭА')
    item1 = types.KeyboardButton('ЛКС')
    item2 = types.KeyboardButton('Посещаемость')
    item3 = types.KeyboardButton('Дисциплины')
    markup.add(item0, item1, item2, item3)
    bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Посещаемость')
def attendance_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton('Таблица посещаемости')
    item2 = types.KeyboardButton('Электронный журнал')
    item3 = types.KeyboardButton('Вернуться в главное меню')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Дисциплины')
def discipline(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item0 = types.KeyboardButton('Философия')
    item1 = types.KeyboardButton('История')
    item2 = types.KeyboardButton('Вернуться в главное меню')
    markup.add(item0, item1, item2)
    bot.send_message(message.chat.id, f"<b>Выберите дисциплину:</b>", parse_mode='html', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Вернуться в главное меню')
def back(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: message.text == 'Таблица посещаемости')
def excel(message):
    bot.send_message(message.chat.id, f"<a href='https://1drv.ms/x/s!AtWlwTRto0UQiia4qC3jQcKhaMfc?e=NLACcc'>Excel Таблица</a>", parse_mode='html')

@bot.message_handler(func=lambda message: message.text == 'Электронный журнал')
def electronic(message):
    bot.send_message(message.chat.id, f"<a href='https://attendance-app.mirea.ru/'>Онлайн журнал</a>", parse_mode='html')

@bot.message_handler(func=lambda message: message.text == 'Философия')
def philosophy(message):
    bot.send_message(message.chat.id, f"<a href='https://docs.google.com/spreadsheets/d/1Vi7DpmFGLSqWtEwTuO5W4PIjS1Ke9HvnT_QXZFks6PY/edit?usp=sharing'>Философия баллы</a>",  parse_mode='html')

@bot.message_handler(func=lambda message: message.text == 'История')
def history(message):
    bot.send_message(message.chat.id,f"<a href=''>История баллы</a>", parse_mode='html')

@bot.message_handler(func=lambda message: message.text == 'ЛКС')
def lks(message):
    bot.send_message(message.chat.id, f"<a href='https://lk.mirea.ru/auth.php'>Личный кабинет студента</a>", parse_mode='html')

@bot.message_handler(func=lambda message: message.text == 'СДО МИРЭА')
def lks(message):
    bot.send_message(message.chat.id, f"<a href='https://login.mirea.ru/login/?next=/oauth2/v1/authorize/%3Fresponse_type%3Dcode%26client_id%3DdnOh7sdtPxfyxzbxcMRLksWlCCE3WsgTfRY6AWKh%26redirect_uri%3Dhttps%253A%252F%252Fonline-edu.mirea.ru%252Flogin%252F%26scope%3Dbasic%2Bstudent'>Система дистанционного обучения</a>", parse_mode='html')

@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.send_message(message.chat.id, f"<i>Повторите попытку</i>", parse_mode='html')

bot.polling(none_stop=True)
