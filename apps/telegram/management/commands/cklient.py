from aiogram import types, Dispatcher
import logging
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from asgiref.sync import sync_to_async

from apps.telegram.state.cklient import ClientStates
from apps.telegram.button.cklient import client_keyboard, back_keyboard, cklient_region_keyboard, comment_keyboard
from apps.telegram.models import Business, Cklient, UserCklient
from apps.telegram.management.commands.bot_instance import bot
import json

accepted_requests = set()
declined_requests = set()
searched_requests = set()

async def edit_message_if_different(callback_query: types.CallbackQuery, new_text: str, new_reply_markup: types.InlineKeyboardMarkup):
    current_text = callback_query.message.text
    current_reply_markup = callback_query.message.reply_markup
    
    current_reply_markup_json = json.dumps(current_reply_markup.to_python() if current_reply_markup else None)
    new_reply_markup_json = json.dumps(new_reply_markup.to_python() if new_reply_markup else None)

    logging.info(f"Сравнение сообщений:\nТекущее сообщение: {current_text}\nНовое сообщение: {new_text}\nТекущая клавиатура: {current_reply_markup_json}\nНовая клавиатура: {new_reply_markup_json}")

    if current_text != new_text or current_reply_markup_json != new_reply_markup_json:
        logging.info("Сообщение будет обновлено.")
        await callback_query.message.edit_text(new_text, reply_markup=new_reply_markup)
    else:
        logging.info("Сообщение не требует обновления.")
        
async def client_start(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info("Команда 'client_start' получена")
    await state.finish()
    await callback_query.answer()
    await edit_message_if_different(
        callback_query,
        "Здравствуйте! ☺️ Я ваш личный помощник по поиску жилья. Укажите ваши предпочтения, и я найду идеальное место для вашего отдыха. Давайте начнем путешествие вместе! 🌍✨\n\n",
        client_keyboard()
    )
    logging.info('переход')

async def choose_region(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info("Команда 'choose_region' получена")
    await ClientStates.choosing_region.set()
    await callback_query.answer()
    await edit_message_if_different(
        callback_query,
        "Пожалуйста, выберите ваш регион:",
        cklient_region_keyboard()
    )

async def region_selected(callback_query: types.CallbackQuery, state: FSMContext):
    logging.info(f"Регион выбран: {callback_query.data}")
    region_map = {
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
        'city_bokon': 'Боконбаева'
    }
    region_text = region_map.get(callback_query.data, 'Неизвестный регион')
    await state.update_data(region=callback_query.data, region_text=region_text)
    await ClientStates.entering_date.set()
    await callback_query.answer()
    await edit_message_if_different(
        callback_query,
        f"Вы выбрали регион: {region_text}. Пожалуйста, введите дату заезда (дд.мм.гггг):",
        back_keyboard()
    )

async def date_entered(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    region = user_data.get('region')
    region_text = user_data.get('region_text')
    date = message.text

    logging.info(f"Дата заезда введена: {date} для региона {region_text}")

    await state.update_data(date=date)
    await ClientStates.entering_comment.set()
    await message.answer("Пожалуйста, оставьте комментарий:", reply_markup=comment_keyboard())

async def comment_entered(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    region_text = user_data.get('region_text')
    date = user_data.get('date')
    comment = message.text

    logging.info(f"Комментарий: {comment}")

    await state.update_data(comment=comment)
    await ClientStates.searching.set()

    search_keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('Поиск', callback_data='search'),
        types.InlineKeyboardButton('Назад', callback_data='choose_date')
    )
    await message.answer("Поиск объявлений...", reply_markup=search_keyboard)

# Обработчик поиска
async def search_action(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    request_id = f"{callback_query.from_user.id}_{user_data.get('region')}_{user_data.get('date')}"
    
    region = user_data.get('region')
    region_text = user_data.get('region_text')
    date = user_data.get('date')
    comment = user_data.get('comment')

    # Сброс состояния для повторного запроса
    if request_id in searched_requests:
        searched_requests.remove(request_id)

    # Сохранение запроса клиента в базу данных
    user_client = await sync_to_async(UserCklient.objects.get)(user_id=callback_query.from_user.id)
    await sync_to_async(Cklient.objects.create)(
        user=user_client,
        region=region_text,
        date=date,
        comment=comment
    )

    # Отправка запроса бизнес-клиентам
    business_clients = await sync_to_async(list)(Business.objects.filter(region=region, is_active=True).select_related('user'))

    if not business_clients:
        await callback_query.answer("Нет активных объявлений в выбранном регионе.", show_alert=True)
    else:
        for business_client in business_clients:
            unique_request_id = f"{business_client.id}_{request_id}"
            if unique_request_id not in searched_requests and unique_request_id not in declined_requests:
                accept_decline_keyboard = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton('❌ Отклонить', callback_data=f'decline_{business_client.id}_{callback_query.from_user.id}'),
                    types.InlineKeyboardButton('✅ Принять', callback_data=f'accept_{business_client.id}_{callback_query.from_user.id}'),
                )
                await bot.send_message(
                    business_client.user.user_id,  # Убедитесь, что поле user_id у вас правильно указано
                    f"Новый запрос от клиента:\n\nРегион: {region_text}\nДата заезда: {date}\nКомментарий: {comment}",
                    reply_markup=accept_decline_keyboard
                )
                searched_requests.add(unique_request_id)
        searched_requests.add(request_id)
        await callback_query.answer("Запрос отправлен бизнес-клиентам в вашем регионе.", show_alert=True)


async def handle_accept(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data.split('_')
    business_id = int(data[1])
    client_id = int(data[2])
    request_id = f"{callback_query.from_user.id}_{business_id}"

    if request_id in accepted_requests or request_id in declined_requests:
        await callback_query.answer("Этот запрос уже был обработан.", show_alert=True)
        return

    accepted_requests.add(request_id)

    business_client = await sync_to_async(Business.objects.get)(id=business_id)

    region_map = {
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
    region_text = region_map.get(business_client.region, 'Неизвестный регион')

    booking_details = (
        f"Регион: {region_text}\n"
        f"Пансионат: {business_client.pansionat}\n"
        f"Тип размещения: {business_client.type_accommodation}\n"
        f"Удобства: {business_client.facilities}\n"
        f"Количество мест: {business_client.quantities}\n"
        f"Цена: {business_client.price} USD\n"
        f"Номер телефона: {business_client.phone_number}\n"
    )

    # Отправляем фотографии с описанием
    if business_client.photos:
        photos = business_client.photos.split(',')  # Предполагается, что фотографии хранятся в виде строки, разделенной запятыми
        media = [types.InputMediaPhoto(media=photo) for photo in photos]
        if media:
            media[0].caption = booking_details  # Добавляем описание к первой фотографии
            await bot.send_media_group(client_id, media)
    else:
        await bot.send_message(client_id, booking_details)

    await callback_query.answer("Запрос принят и информация отправлена клиенту.", show_alert=True)

    # Обновление сообщения с кнопками
    await callback_query.message.edit_reply_markup(types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('✅ Принято', callback_data='accepted')
    ))

    # Отправляем сообщение клиенту с предложением поиска в другом районе
    search_other_region_keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('Поиск в другом районе', callback_data='search_other_region')
    )
    await bot.send_message(
        client_id,
        "Запрос был принят. Вы можете продолжить поиск в другом районе.",
        reply_markup=search_other_region_keyboard
    )

async def handle_decline(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data.split('_')
    business_id = int(data[1])
    client_id = int(data[2])
    request_id = f"{callback_query.from_user.id}_{business_id}"

    if request_id in accepted_requests or request_id in declined_requests:
        await callback_query.answer("Этот запрос уже был обработан.", show_alert=True)
        return

    declined_requests.add(request_id)
    await callback_query.message.delete()
    await callback_query.answer("Запрос был отклонен и сообщение удалено.", show_alert=True)

async def search_other_region(callback_query: types.CallbackQuery, state: FSMContext):
    await choose_region(callback_query, state)

async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    logging.info(f"Команда 'go_back' получена, текущее состояние: {current_state}")
    if current_state == ClientStates.entering_comment.state:
        await ClientStates.entering_date.set()
        await callback_query.answer()
        await edit_message_if_different(
            callback_query,
            "Вы выбрали регион. Пожалуйста, введите дату заезда (дд.мм.гггг):",
            back_keyboard()
        )
    elif current_state == ClientStates.entering_date.state:
        await choose_region(callback_query, state)
    else:
        await client_start(callback_query, state)

def register_handlers_client(dp: Dispatcher):
    dp.register_callback_query_handler(client_start, Text(equals='client_start'), state='*')
    dp.register_callback_query_handler(choose_region, Text(equals='choose_region'), state='*')
    dp.register_callback_query_handler(region_selected, Text(startswith='city_'), state=ClientStates.choosing_region)
    dp.register_callback_query_handler(go_back, Text(equals='choose_date'), state='*')  # Изменено для правильной работы кнопки "Назад"
    dp.register_callback_query_handler(search_action, Text(equals='search'), state=ClientStates.searching)
    dp.register_callback_query_handler(handle_accept, Text(startswith='accept_'), state='*')
    dp.register_callback_query_handler(handle_decline, Text(startswith='decline_'), state='*')
    dp.register_callback_query_handler(search_other_region, Text(equals='search_other_region'), state='*')
    dp.register_message_handler(date_entered, state=ClientStates.entering_date)
    dp.register_message_handler(comment_entered, state=ClientStates.entering_comment)