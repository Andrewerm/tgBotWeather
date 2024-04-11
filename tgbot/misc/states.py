from aiogram.fsm.state import StatesGroup, State


class ProfileFSM(StatesGroup):
    name = State()
    profession = State()
    filled = State()
