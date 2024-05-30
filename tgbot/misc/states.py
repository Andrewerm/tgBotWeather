from aiogram.fsm.state import StatesGroup, State


class ProfileFSM(StatesGroup):
    name = State()
    profession = State()
    filled = State()


class CreatePostFSM(StatesGroup):
    new_post = State()
    date_pick = State()
    time_pick = State()
