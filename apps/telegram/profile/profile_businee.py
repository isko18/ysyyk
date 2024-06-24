import logging
from aiogram import types, Dispatcher
from asgiref.sync import sync_to_async
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from apps.telegram.models import Business, UserBusiness

REGION_NAMES = {
        'city_balykchy': 'Балыкчы',
        'city_tamchy': 'Тамчы',
        'city_chok_tal': 'Чок-Тал',
        'city_chon_saroi': 'Чон-Сары-Ой',
        'city_saroi': 'Сары-Ой',
        'city_cholponata': 'Чолпон-Ата',
        'city_bosteri': 'Бостери',
        'city_ananeva': 'Ананьево',
        'city_tup': 'Тюп',
        'city_karakol': 'Каракол',
        'city_jetiogyz': 'Джети Огуз',
        'city_kyzyl': 'Кызыл Суу',
        'city_tamga': 'Тамга',
        'city_bokon': 'Боконбаева',
        'city_baktyy':'Бактуу-Долоноту',
        'city_koshkol' : 'Кош-Кол',
        'city_ornok' : 'Орнок',
        'city_karaoi' : 'Кара-Ой',
        'city_chyrpykty' : 'Чырпыкты',
        'city_baet' : 'Бает',
    }

def create_back_button(callback_data='back'):
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Назад', callback_data=callback_data))

async def profile_busness(query: types.CallbackQuery):
    user_id = query.from_user.id
    username = query.from_user.username

    profile_text = f"""
    Ваш профиль:
    ID: {user_id}
    Username: {username}
    """

    keyboard = InlineKeyboardMarkup()
    if username.startswith('busness_'):
        keyboard.add(InlineKeyboardButton('Поиск отеля', callback_data='search'))
        profile_text += "\n\nВы клиент и не можете размещать объявления отелей."
    else:
        keyboard.add(InlineKeyboardButton('Мои объявления', callback_data='my_ads_busness'))

    keyboard.add(InlineKeyboardButton('Назад', callback_data='business_start'))

    await query.message.edit_text(profile_text, reply_markup=keyboard)

async def my_ads_busness(query: types.CallbackQuery):
    user_id = query.from_user.id

    try:
        # Получение пользователя по user_id
        user_business = await sync_to_async(UserBusiness.objects.get)(user_id=user_id)

        # Получение всех объявлений пользователя
        ads = await sync_to_async(list)(Business.objects.filter(user=user_business))

        if not ads:
            no_ads_text = "У вас нет объявлений."
            await query.message.edit_text(no_ads_text, reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton('Назад', callback_data='profile_busness'),
                InlineKeyboardButton('Разместить еще', callback_data='business_start')
            ))
            return

        for booking in ads:
            region_name = REGION_NAMES.get(booking.region, 'Неизвестный регион')
            ad_text = f"""
- Регион: {region_name}
- Пансионат: {booking.pansionat}
- Тип размещения: {booking.type_accommodation}
- Удобства: {booking.facilities}
- Количество мест: {booking.quantities}
- Цена: {booking.price} USD
- Номер телефона: {booking.phone_number}
- Активен: {"Да" if booking.is_active else "Нет"}
\n"""
            photos = booking.photos.split(',')
            media = [types.InputMediaPhoto(photo, caption=ad_text if idx == 0 else "") for idx, photo in enumerate(photos)]

            await query.bot.send_media_group(query.message.chat.id, media)

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Назад', callback_data='profile_busness'))
        keyboard.add(InlineKeyboardButton('Разместить еще', callback_data='business_start'))

        await query.bot.send_message(query.message.chat.id, "Вы можете вернуться назад или разместить еще одно объявление.", reply_markup=keyboard)

    except UserBusiness.DoesNotExist:
        await query.message.edit_text("Пользователь не найден.", reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Назад', callback_data='profile_busness')
        ))
    except Exception as e:
        logging.error(f"Error while fetching ads: {e}")
        error_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Назад', callback_data='profile_busness'))
        await query.message.edit_text("Произошла ошибка при получении ваших объявлений.", reply_markup=error_keyboard)