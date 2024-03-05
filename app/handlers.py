from aiogram import F, Router, types, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputFile
import emoji
import app.keyboards as kb
from random import randint

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) :
    await message.reply(f'Добро пожаловать, {message.from_user.full_name}', reply_markup=kb.main)



@router.callback_query(F.data == 'attedance')
async def attedance_message(callback: CallbackQuery):
    await callback.answer('mirea')
    await callback.message.edit_text(f'⬇  Выберите один из пунктов  ⬇', reply_markup=kb.attedance_list)


@router.callback_query(F.data == 'lks')
async def lks_message(callback: CallbackQuery):
    await callback.answer('lks')
    await callback.message.edit_text(f'Личный кабинет студента', reply_markup=kb.lks_list)


@router.callback_query(F.data == 'cdo')
async def cdo_message(callback: CallbackQuery):
    await callback.answer('cdo')
    await callback.message.edit_text(f'Система дистанционного обучения', reply_markup=kb.cdo_list)



@router.callback_query(F.data == 'discipline')
async def discipline_message(callback: CallbackQuery):
    await callback.answer('discipline')
    await callback.message.edit_text(f'⬇  Выберите дисциплину  ⬇', reply_markup=kb.discipline_list)


@router.callback_query(F.data == 'other')
async def other_message(callback: CallbackQuery):
    await callback.answer('other')
    await callback.message.edit_text(f'Выберите из предложенного', reply_markup=kb.other_list)


@router.callback_query(F.data == 'back')
async def back_message(callback: CallbackQuery):
    await callback.answer('back')
    await callback.message.edit_text(f'Вы вернулись в главное меню  ✔️', reply_markup=kb.main)


@router.callback_query(F.data == 'group')
async def group_list(callback: CallbackQuery):
    await callback.answer('ЭФБО-07-23')
    await callback.message.edit_text(f'''
<b>🩸ЭФБО-07-23 🩸</b>
<i>1. Балыбердин И. А.
2. Бузин М. А.
3. Ведищев Е. М.
4. Воротынцев Д. А.
5. Голубев Г. Д.
6. <a href='https://youtu.be/8rUPngAbWRs'>Дорошенко В. П.</a>
7. <a href='https://youtu.be/dQw4w9WgXcQ?si=EF8IiRftuaj64V2s'>Дремов М. И.</a>
8. Дубов К. А.
9. Егоров А. П.
10. Елисеев Я. А.
11. Измайлова А. А.
12. Комов А. Д.
13. Кудяшова М. И.
14. Ларин А. В.
15. Леонтьев Д. С.
16. Манасян А. Р.
17. Местаев Р. Р.
18. Минаев Д. В.
19. Михайлов С. К.
20. Мищенко А. П.
21. Мусели Д. З.
22. Насыров Е. О.
23. Огилько В. Н.
24. Погосов В. Э.
25. Прокошин К. Д.
26. Силинский М. А.
27. <a href='https://www.youtube.com/watch?v=50nlHgRYp1I&t=82s'>Смирнов Е. А.</a>
28. Сорокин Я. А.
29. Тадевосян А. А.
30. Тихонов Г. А.
31. Умнов М. Д.
32. Червяков В. С.
33. Черний Г. А.
34. Чистопрудов В. С.
35. Шляшин Д. А.
36. Шульга Н. А.</i>
    ''', reply_markup=kb.group_list, parse_mode='html', disable_web_page_preview=True)


@router.callback_query(F.data == 'birthday')
async def birthday_list(callback: CallbackQuery):
    await callback.answer('че забыл, да?')
    await callback.message.edit_text(f'''
<i><b>Зима</b></i> 🥶🥶🥶
                                     
    <u>Декабрь:</u>
        Смирнов Егор 10.12.2005
        Голубев Григорий 14.12.2005
        Насыров Егор 16.12.2005
        Червяков Валерий 28.12.2004 
                                                                
    <u>Январь:</u>
        Елисеев Ярослав 01.01.2006
        Тихонов Герман 06.01.2006
        Кудяшова Мария 10.01.2006
                                     
    <u>Февраль:</u>
        Минаев Даниил 12.02.2005
        Воротынцев Даниил 18.02.2003
                                     
<i><b>Весна</b></i> 🍀🍀🍀
                                     
    <u>Март:</u>
        Дубов Кирилл 30.03.2005
                                     
    <u>Апрель:</u>                              
        Черний Глеб 08.04.2005
        Дмитрий Леонтьев 08.04.2005
        Умнов Михаил 09.04.2005
        Местаев Рамзан 11.04.2005
        Дорошенко Вячеслав 15.04.2005
        Чистопрудов Владимир 22.04.2005
                                     
    <u>Май:</u>
        Манасян Ашот 03.05.2005
        Ларин Артемий 18.05.2005
        Прокошин Кирилл 24.05.2005
        Артем Егоров 25.05.2005
                                     
<i><b>Лето</b></i> 🌡️🌡️🌡️

    <u>Июнь:</u>
        Силинский Михаил 07.06.2005
        Тадевосян Артак 11.06.2005
        Шульга Николай 22.06.2005
        Ведищев Елисей 27.06.2005

    <u>Июль:</u>       
        Измайлова Арина 23.07.2005
        Огилько Владислав 27.07.2005

    <u>Август:</u>
        Сорокин Ярослав 23.08.2005

<i><b>Осень</b></i> 🍁🍁🍁

    <u>Сентябрь:</u>
        Михайлов Сергей 04.09.2005

    <u>Октябрь:</u>
        Погосов Вячеслав 05.10.2005
        Мищенко Анна 05.10.2005

    <u>Ноябрь:</u>
        Шляшин Дмитрий 12.11.2005
        Дремов Михаил 16.11.2004
        Мусели Джами 18.11.2004
        Комов Андрей 22.11.2005
        Балыбердин Иван 30.11.2005
    ''', reply_markup=kb.bth_list, parse_mode='html')


@router.callback_query(F.data == 'back_other')
async def back_menu(callback: CallbackQuery):
    await callback.answer('back')
    await callback.message.edit_text(f'Вы вернулись  ✔️', reply_markup=kb.other_list)

@router.callback_query(F.data == 'random')
async def randomyzer(callback: CallbackQuery):
    await callback.answer('randomyzer')
    await callback.message.answer(f'Выберите диапозон допустимых значений', reply_markup=kb.random_list)

@router.message(F.text == '1 - 2  ⚧️')
async def rand_1(message: Message):
    await message.answer(f'<i>Ваше число: {randint(1, 2)}</i>', parse_mode='html')


@router.message(F.text == '0 - 100  ⚧️')
async def rand_2(message: Message):
    await message.answer(f'<i>Ваше число: {randint(0, 100)}</i>', parse_mode='html')


@router.message(F.text == '0 - 1000  ⚧️')
async def rand_3(message: Message):
    await message.answer(f'<i>Ваше число: {randint(0, 1000)}</i>', parse_mode='html')


@router.message(F.text == '0 - 10000  ⚧️')
async def rand_4(message: Message):
    await message.answer(f'<i>Ваше число: {randint(0, 10000)}</i>', parse_mode='html')


@router.message(F.text=='Назад  🔹')
async def back_other(message: Message):
    await message.answer('Вы вернулись назад  ✔️', reply_markup=kb.other_list)


@router.message(F.text == 'пошел нахуй')
async def none(message: Message):
    await message.answer(f'Сам иди нахуй, чушпан')


@router.message(F.text == 'пидор')
async def none(message: Message):
    await message.answer(f'А может ты пидор?')


@router.message(F.text == 'лох')
async def none(message: Message):
    await message.answer(f'{message.from_user.first_name}, завязывай с этой хуйней')


@router.message(F.text)
async def none(message: Message):
    await message.answer(f'{message.from_user.full_name}, это тебе не гпт, повтори попытку')
