from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.config import load_config
from tgbot.misc.states import ProfileFSM

posts_router = Router()

config = load_config()


@posts_router.message(Command('posts'))
async def get_weather_location(message: Message, state: FSMContext):
    await state.set_state(ProfileFSM.new_post)
    await message.reply('Наберите пост для публикации')


@posts_router.message(StateFilter(ProfileFSM.new_post))
async def new_post(message: Message):
    await message.reply('Пост принят в обработку')
