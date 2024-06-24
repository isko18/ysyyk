from aiogram import types

def business_keyboard():
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

def create_start_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Выбрать регион', callback_data='сontinue'))
    keyboard.add(types.InlineKeyboardButton('Бизнес профиль', callback_data='profile_busness'))
    return keyboard

accommodation_types = ['Квартира', 'Танхаус', 'Пентхаус', 'Юрта', ' Коттедж', 'Кемпинг']

def create_accommodation_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for acc_type in accommodation_types:
        keyboard.add(types.InlineKeyboardButton(acc_type, callback_data=f'acc_{acc_type}'))
    return keyboard


amenities = ['Питание', 'Кондиционер', 'Стиральная машина', 'Утюг', 'Балкон', 'Wi-Fi', 'Бассейн', 'Парковка', 'Фитнес-зал', 'Душ', 'Cанузел', 'Холодильник', 'Cейф', 'ТВ', 'Баня', 'Зона барбекю']

def create_amenities_keyboard(selected_amenities):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for amenity in amenities:
        text = f"✅ {amenity}" if amenity in selected_amenities else amenity
        keyboard.insert(types.InlineKeyboardButton(text, callback_data=f'amenity_{amenity}'))
    keyboard.add(types.InlineKeyboardButton('Готово', callback_data='done_selecting_amenities'))
    keyboard.add(types.InlineKeyboardButton('Назад', callback_data='back_to_accommodation_type'))
    return keyboard