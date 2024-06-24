from aiogram.dispatcher.filters.state import State, StatesGroup

class ClientStates(StatesGroup):
    choosing_region = State()
    entering_date = State()
    entering_comment = State()
    checking_referral = State()
    searching = State()