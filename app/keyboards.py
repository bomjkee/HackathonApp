from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,  InlineKeyboardMarkup, InlineKeyboardButton
import emoji

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посещаемость  🚩', callback_data='attedance'), InlineKeyboardButton(text='Другое  💱', callback_data='other')],
    [InlineKeyboardButton(text='ЛКС 🏴', callback_data='lks'), InlineKeyboardButton(text='Дисциплины', callback_data='discipline'), 
     InlineKeyboardButton(text='СДО 🏳️', callback_data='cdo')]
])


attedance_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Таблица посещаемости', url='https://1drv.ms/x/s!AtWlwTRto0UQiia4qC3jQcKhaMfc?e=NLACcc')],
    [InlineKeyboardButton(text='Журнал посещаемости', url='https://attendance-app.mirea.ru/')],
    [InlineKeyboardButton(text='Назад', callback_data='back')]
])


cdo_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🌐🌐🌐', url='https://online-edu.mirea.ru/')],
    [InlineKeyboardButton(text='Назад  🔹', callback_data='back')]
])


lks_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⚕️⚕️⚕️', url='https://lk.mirea.ru/auth.php')],
    [InlineKeyboardButton(text='Назад  🔹', callback_data = 'back')]
])


discipline_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Философия', 
     url='https://docs.google.com/spreadsheets/d/1Vi7DpmFGLSqWtEwTuO5W4PIjS1Ke9HvnT_QXZFks6PY/edit?usp=sharing')],
    #[InlineKeyboardButton(text='История', url='')], 
    [InlineKeyboardButton(text='Назад  🔹', callback_data='back')]
])


other_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посмотреть список группы  ♂️', callback_data='group')],
    [InlineKeyboardButton(text='Дни рождения  🪐', callback_data='birthday')],
    [InlineKeyboardButton(text='Рандомайзер чисел  ♨️', callback_data='random')],
    [InlineKeyboardButton(text='Назад  🔹', callback_data='back')]
])

group_list = InlineKeyboardMarkup(inline_keyboard= [
    [InlineKeyboardButton(text='Назад  🔹', callback_data='back_other')]
])

bth_list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад  🔹', callback_data='back_other')]
])

random_list = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='1 - 2  ⚧️'), KeyboardButton(text='0 - 100  ⚧️')],
    [KeyboardButton(text='0 - 1000  ⚧️'), KeyboardButton(text='0 - 10000  ⚧️')],
    [KeyboardButton(text='Назад  🔹')]
], resize_keyboard=True, one_time_keyboard=True)
