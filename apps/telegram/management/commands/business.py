import logging
from aiogram import types, Dispatcher
import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
import asyncio

from apps.telegram.button.business import (
    create_amenities_keyboard, create_start_keyboard, business_keyboard,
    create_accommodation_keyboard
)
from apps.telegram.models import Business, UserBusiness, UserCklient
from apps.telegram.state.business import BusinessForm
from apps.telegram.profile.profile_businee import profile_busness, my_ads_busness
from apps.telegram.management.commands.bot_instance import bot

# Registration function for business users
async def register_business_user(user_id, username, referrer_id=None):
    await sync_to_async(UserBusiness.objects.create)(
        user_id=user_id,
        username=username
    )

# Registration function for client users
async def register_client_user(user_id, username, referrer_id=None):
    await sync_to_async(UserCklient.objects.create)(
        user_id=user_id,
        username=username
    )

# Function to create a back button
def create_back_button(callback_data='back'):
    return InlineKeyboardMarkup().add(InlineKeyboardButton('Назад', callback_data=callback_data))

# Handlers for profile and ads for business users
async def handle_profile_busness(query: types.CallbackQuery):
    await profile_busness(query)

async def handle_my_ads_busness(query: types.CallbackQuery):
    await my_ads_busness(query)

# Start command handler
async def start(message: types.Message):
    logging.info("Команда /start получена")
    user_id = message.from_user.id
    username = message.from_user.username
    referrer_id = message.get_args()

    user_business = await sync_to_async(UserBusiness.objects.filter(user_id=user_id).first)()
    user_client = await sync_to_async(UserCklient.objects.filter(user_id=user_id).first)()
    
    if user_business is None and user_client is None:
        await register_business_user(user_id, username, referrer_id)
        await register_client_user(user_id, username, referrer_id)

    await message.answer(
        "Здравствуйте! Выберите тип пользователя:",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Я клиент 🔍', callback_data='client_start'),
            InlineKeyboardButton('Я сдаю 🏠', callback_data='business_start')
        )
    )

async def back_to_start(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()  # Reset the state
    await start(callback_query.message)
    logging.info("Возврат к началу")

async def business_start(callback_query: types.CallbackQuery):
    logging.info("Callback business_start получен")
    keyboard = create_start_keyboard().add(InlineKeyboardButton('Назад', callback_data='back_to_start'))
    await callback_query.message.edit_text(
        """Вас приветствует бизнес ассистент, я помогу вам создать ваше объявление""",
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN
    )
    logging.info("Сообщение business_start успешно отправлено")

async def continue_handler(callback_query: types.CallbackQuery):
    logging.info("Callback continue получен")
    keyboard = business_keyboard().add(InlineKeyboardButton('Назад', callback_data='business_start'))
    await callback_query.message.edit_text("Выберите район:", reply_markup=keyboard)
    await BusinessForm.region.set()
    logging.info("Ожидается выбор региона")

async def process_region(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['region'] = callback_query.data
    await BusinessForm.next()
    await callback_query.message.edit_text("Введите название места отдыха:", reply_markup=create_back_button('back_to_region'))
    logging.info("Вы выбрали район, ждем название пансионата")

async def back_to_region(callback_query: types.CallbackQuery, state: FSMContext):
    await BusinessForm.region.set()
    await callback_query.message.edit_text("Выберите район:", reply_markup=business_keyboard().add(InlineKeyboardButton('Назад', callback_data='back_to_start')))
    logging.info("Возврат к выбору региона")

async def process_pansionat(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['pansionat'] = message.text
    await BusinessForm.next()
    await message.answer("Выберите тип размещения:", reply_markup=create_accommodation_keyboard().add(InlineKeyboardButton('Назад', callback_data='back_to_pansionat')))
    logging.info("Ожидается выбор типа размещения")

async def back_to_pansionat(callback_query: types.CallbackQuery, state: FSMContext):
    await BusinessForm.pansionat.set()
    await callback_query.message.edit_text("Введите название пансионата:", reply_markup=create_back_button('back_to_region'))
    logging.info("Возврат к вводу названия пансионата")

async def process_accommodation_type(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['accommodation_type'] = callback_query.data[4:]
    await BusinessForm.next()
    await ask_amenities(callback_query.message)
    logging.info("Ожидается выбор удобств")

async def ask_amenities(message: types.Message):
    keyboard = create_amenities_keyboard([])
    await message.answer("Выберите удобства (можно выбрать несколько):", reply_markup=keyboard)
    await BusinessForm.amenities.set()

async def back_to_accommodation_type(callback_query: types.CallbackQuery, state: FSMContext):
    await BusinessForm.accommodation_type.set()
    await callback_query.message.edit_text("Выберите тип размещения:", reply_markup=create_accommodation_keyboard().add(InlineKeyboardButton('Назад', callback_data='back_to_pansionat')))
    logging.info("Возврат к выбору типа размещения")

async def select_amenity(query: types.CallbackQuery, state: FSMContext):
    amenity = query.data.split('_')[1]
    data = await state.get_data()
    selected_amenities = data.get('selected_amenities', [])
    if amenity not in selected_amenities:
        selected_amenities.append(amenity)
        logging.info(f"Услуга '{amenity}' выбрана")
    else:
        selected_amenities.remove(amenity)
        logging.info(f"Услуга '{amenity}' отменена")
    await state.update_data(selected_amenities=selected_amenities)
    keyboard = create_amenities_keyboard(selected_amenities)
    await query.message.edit_reply_markup(reply_markup=keyboard)
    await query.answer(f"Удобство {amenity} выбрано")

async def done_selecting_amenities(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        selected_amenities = data['selected_amenities']
        amenities_text = '\n'.join(selected_amenities)

    # Send a message with the selected amenities
    await query.message.answer(f"Вы выбрали следующие удобства:\n\n{amenities_text}")

    # Send a separate message prompting for the number of places
    await query.message.answer("Введите количество мест в формате 5-9:", reply_markup=create_back_button('back_to_amenities'))
    
    await BusinessForm.next()
    logging.info("Ожидается ввод количества мест")

async def back_to_amenities(callback_query: types.CallbackQuery, state: FSMContext):
    await ask_amenities(callback_query.message)

async def process_number_of_places(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number_of_places'] = message.text
    await BusinessForm.next()
    await message.answer("Введите цену в долларах:", reply_markup=create_back_button('back_to_number_of_places'))
    logging.info("Ожидается ввод цены")

async def back_to_number_of_places(callback_query: types.CallbackQuery, state: FSMContext):
    await BusinessForm.number_of_places.set()
    await callback_query.message.edit_text("Введите количество мест в формате 5-9:", reply_markup=create_back_button('back_to_amenities'))
    logging.info("Возврат к вводу количества мест")

async def process_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await BusinessForm.next()
    await message.answer("Введите номер телефона, начиная с +996:", reply_markup=create_back_button('back_to_price'))
    logging.info("Ожидается ввод номера телефона")

async def back_to_price(callback_query: types.CallbackQuery, state: FSMContext):
    await BusinessForm.price.set()
    await callback_query.message.edit_text("Введите цену в долларах:", reply_markup=create_back_button('back_to_number_of_places'))
    logging.info("Возврат к вводу цены")

async def process_phone_number(message: types.Message, state: FSMContext):
    if not message.text.startswith('+996'):
        await message.answer("Номер телефона должен начинаться с +996. Попробуйте еще раз:", reply_markup=create_back_button('back_to_price'))
        return
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await BusinessForm.next()
    sent_message = await message.answer("Пожалуйста, загрузите от 5 до 10 фотографий.", reply_markup=create_back_button('back_to_phone_number'))
    async with state.proxy() as data:
        data['photo_message_id'] = sent_message.message_id
    logging.info("Ожидается загрузка фотографий")

async def back_to_phone_number(callback_query: types.CallbackQuery, state: FSMContext):
    await BusinessForm.phone_number.set()
    await callback_query.message.edit_text("Введите номер телефона, начиная с +996:", reply_markup=create_back_button('back_to_price'))
    logging.info("Возврат к вводу номера телефона")

async def process_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])

    new_photo = message.photo[-1].file_id
    photos.append(new_photo)
    await state.update_data(photos=photos)

    message_text = f"Фото загружено. Загрузите еще фото или нажмите 'Завершить' для завершения."

    chat_id = message.chat.id
    photo_message_id = data.get('photo_message_id')

    # Удаляем предыдущее сообщение, если оно существует
    if photo_message_id:
        await message.bot.delete_message(chat_id, photo_message_id)

    msg = await message.answer(
        message_text,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Завершить', callback_data='finish_photos'),
            InlineKeyboardButton('Назад', callback_data='back_to_phone_number'),
            InlineKeyboardButton('Разместить отель', callback_data='register_hotel')
        )
    )
    await state.update_data(photo_message_id=msg.message_id)

async def finish_photos_handler(query: types.CallbackQuery, state: FSMContext):
    await query.answer("Пожалуйста, используйте кнопку 'Разместить отель' для завершения.")
    await register_hotel_handler(query, state)

async def register_hotel_handler(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = query.from_user.id

    async with state.proxy() as data:
        user_business = await sync_to_async(UserBusiness.objects.filter(user_id=user_id).first)()

        if not user_business:
            await query.message.answer("Ошибка: Пользователь не найден в системе. Пожалуйста, зарегистрируйтесь заново.")
            await state.finish()
            return

        region = data.get('region')
        pansionat = data.get('pansionat')
        accommodation_type = data.get('accommodation_type')
        selected_amenities = data.get('selected_amenities')
        number_of_places = data.get('number_of_places')
        price = data.get('price')
        phone_number = data.get('phone_number')
        photos = data.get('photos')

        await sync_to_async(Business.objects.create)(
            user=user_business,
            region=region,
            pansionat=pansionat,
            type_accommodation=accommodation_type,
            facilities=', '.join(selected_amenities) if selected_amenities else '',
            quantities=number_of_places,
            price=price,
            phone_number=phone_number,
            photos=','.join(photos) if photos else '',
            is_active=False
        )

    await state.finish()
    await query.message.answer(
        "Спасибо! Ваше объявление было создано и сохранено.",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Разместить еще одно объявление', callback_data='business_start')
        )
    )
    logging.info("Фотографии получены")

async def back_to_photos_handler(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    remaining_photos = 10 - len(photos)
    message_text = f"Фото {len(photos)}/10 загружено. Загрузите еще {remaining_photos} фото или нажмите 'Завершить' для завершения."

    await query.message.edit_text(
        message_text,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('Завершить', callback_data='finish_photos'),
            InlineKeyboardButton('Назад', callback_data='back_to_phone_number'),
            InlineKeyboardButton('Разместить отель', callback_data='register_hotel')
        )
    )

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_callback_query_handler(profile_busness, lambda query: query.data == 'profile_busness')
    dp.register_callback_query_handler(my_ads_busness, lambda query: query.data == 'my_ads_busness')
    dp.register_callback_query_handler(back_to_start, lambda c: c.data == 'back_to_start', state='*')
    dp.register_callback_query_handler(business_start, lambda c: c.data == 'business_start')
    dp.register_callback_query_handler(continue_handler, lambda c: c.data == 'сontinue', state='*')
    dp.register_callback_query_handler(process_region, lambda c: c.data.startswith('city_'), state=BusinessForm.region)
    dp.register_callback_query_handler(back_to_region, lambda c: c.data == 'back_to_region', state=BusinessForm.pansionat)
    dp.register_message_handler(process_pansionat, state=BusinessForm.pansionat)
    dp.register_callback_query_handler(back_to_pansionat, lambda c: c.data == 'back_to_pansionat', state=BusinessForm.accommodation_type)
    dp.register_callback_query_handler(process_accommodation_type, lambda c: c.data.startswith('acc_'), state=BusinessForm.accommodation_type)
    dp.register_callback_query_handler(back_to_accommodation_type, lambda c: c.data == 'back_to_accommodation_type', state=BusinessForm.amenities)
    dp.register_callback_query_handler(select_amenity, lambda query: query.data.startswith('amenity_'), state=BusinessForm.amenities)
    dp.register_callback_query_handler(done_selecting_amenities, lambda query: query.data == 'done_selecting_amenities', state=BusinessForm.amenities)
    dp.register_callback_query_handler(back_to_amenities, lambda c: c.data == 'back_to_amenities', state=BusinessForm.number_of_places)
    dp.register_message_handler(process_number_of_places, state=BusinessForm.number_of_places)
    dp.register_callback_query_handler(back_to_number_of_places, lambda c: c.data == 'back_to_number_of_places', state=BusinessForm.price)
    dp.register_message_handler(process_price, state=BusinessForm.price)
    dp.register_callback_query_handler(back_to_price, lambda c: c.data == 'back_to_price', state=BusinessForm.phone_number)
    dp.register_message_handler(process_phone_number, state=BusinessForm.phone_number)
    dp.register_callback_query_handler(back_to_phone_number, lambda c: c.data == 'back_to_phone_number', state=BusinessForm.photos)
    dp.register_message_handler(process_photos, state=BusinessForm.photos, content_types=types.ContentType.PHOTO)
    dp.register_callback_query_handler(finish_photos_handler, lambda query: query.data == 'finish_photos', state=BusinessForm.photos)
    dp.register_callback_query_handler(register_hotel_handler, lambda query: query.data == 'register_hotel', state=BusinessForm.photos)
    dp.register_callback_query_handler(back_to_photos_handler, text='back_to_photos', state='*')
