from aiogram import Router, F
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.config import load_config
from tgbot.keyboards.profile import keyboard_cancel
from tgbot.misc.callback import ProfileNameCallback
from tgbot.misc.states import ProfileFSM

profile_router = Router()

config = load_config()


@profile_router.message(CommandStart())
async def first_question(message: Message, state: FSMContext) -> None:
    markup = keyboard_cancel(message)
    await message.answer('Ты кто? Напиши своё имя, по братски 🙂', reply_markup=markup)
    await state.set_state(ProfileFSM.name)


@profile_router.message(~F.text.startswith('/'), F.text, StateFilter(ProfileFSM.name))
async def set_name(message: Message, state: FSMContext) -> None:
    """ Принимает имя пользователя """
    name = message.text
    await state.update_data({'profile_name': name})
    await message.reply(f"Очень приятно, {name}. Я  - Петя")
    markup = keyboard_cancel(message)
    await message.answer(f'{name}, а ты кто по жизни? 🫤', reply_markup=markup)
    await state.set_state(ProfileFSM.profession)


@profile_router.message(~F.text.startswith('/'), F.text, StateFilter(ProfileFSM.profession))
async def set_profession(message: Message, state: FSMContext) -> None:
    """ Принимает профессию пользователя """
    profession = message.text
    await state.update_data({'profile_profession': profession})
    name = config.tg_bot.bot_names[0]
    await message.reply(f"Круто! А я робот {name} 🤖")
    await state.set_state(ProfileFSM.filled)


@profile_router.callback_query(ProfileNameCallback.filter())
async def callback_set_anonymous(query: CallbackQuery, callback_data: ProfileNameCallback, state: FSMContext):
    if query.from_user.id == callback_data.user_id:
        await state.set_state(None)
        await query.answer()
        if query.message and hasattr(query.message, 'answer'):
            await query.message.answer('Ну ок 🫤')
