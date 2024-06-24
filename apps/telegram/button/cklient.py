# Обновленные клавиатуры
from aiogram import types


def client_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton('Выбрать регион', callback_data='choose_region'),
        types.InlineKeyboardButton('Назад', callback_data='back_to_start')
    )
    return keyboard

def cklient_region_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton('Балыкчы', callback_data='city_balykchy'),
        types.InlineKeyboardButton('Тамчы', callback_data='city_tamchy')
    )
    keyboard.add(
        types.InlineKeyboardButton('Чок-Тал', callback_data='city_chok_tal'),
        types.InlineKeyboardButton('Чон-Сары-Ой', callback_data='city_chon_saroi')
    )
    keyboard.add(
        types.InlineKeyboardButton('Сары-Ой', callback_data='city_saroi'),
        types.InlineKeyboardButton('Чолпон-Ата', callback_data='city_cholponata')
    )
    keyboard.add(
        types.InlineKeyboardButton('Бостери', callback_data='city_bosteri'),
        types.InlineKeyboardButton('Ананьево', callback_data='city_ananeva')
    )
    keyboard.add(
        types.InlineKeyboardButton('Тюп', callback_data='city_tup'),
        types.InlineKeyboardButton('Каракол', callback_data='city_karakol')
    )
    keyboard.add(
        types.InlineKeyboardButton('Джети Огуз', callback_data='city_jetiogyz'),
        types.InlineKeyboardButton('Кызыл Суу', callback_data='city_kyzyl')
    )
    keyboard.add(
        types.InlineKeyboardButton('Тамга', callback_data='city_tamga'),
        types.InlineKeyboardButton('Боконбаева', callback_data='city_bokon')
    )
    keyboard.add(
        types.InlineKeyboardButton('Бактуу-Долоноту', callback_data='city_baktyy'),
        types.InlineKeyboardButton('Кош-Кол', callback_data='city_koshkol')
    )
    keyboard.add(
        types.InlineKeyboardButton('Орнок', callback_data='city_ornok'),
        types.InlineKeyboardButton('Кара-Ой', callback_data='city_karaoi')
    )
    keyboard.add(
        types.InlineKeyboardButton('Чырпыкты', callback_data='city_chyrpykty'),
        types.InlineKeyboardButton('Бает', callback_data='city_baet')
    )
    keyboard.add(
        types.InlineKeyboardButton('Корумду', callback_data='city_korymdy'),
    )
    return keyboard
def back_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='choose_region'))
    return keyboard

def comment_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='choose_date'))
    return keyboard

def referral_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton('Отправить', callback_data='send_referral'),
        types.InlineKeyboardButton('Назад', callback_data='enter_comment'),
        types.InlineKeyboardButton('Поиск', callback_data='search')
    )
    return keyboard