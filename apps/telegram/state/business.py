from aiogram.dispatcher.filters.state import State, StatesGroup

class BusinessForm(StatesGroup):
    region = State()
    pansionat = State()
    accommodation_type = State()
    amenities = State()
    number_of_places = State()
    price = State()
    phone_number = State()
    photos = State()