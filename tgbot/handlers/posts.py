import time

from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.config import load_config
from tgbot.keyboards.posts import send_post_kb
from tgbot.misc.callback import SendPostNowCallback, SendPostDelayCallback
from tgbot.misc.states import CreatePostFSM
from tgbot.services.posts_data_store import PostsStoreHandler, PostInfoData, PostStatus

posts_router = Router()

config = load_config()


@posts_router.message(Command('posts'))
async def get_weather_location(message: Message, state: FSMContext):
    await state.set_state(CreatePostFSM.new_post)
    await message.reply('Наберите пост для публикации')


@posts_router.message(StateFilter(CreatePostFSM.new_post))
async def new_post(message: Message, state: FSMContext):
    """ Создан новый пост """
    # Создаем копию оригинального сообщения в этом же чате пользователя
    copied_message = await message.copy_to(message.chat.id)
    # создаём управляющее сообщение
    manage_message = await message.answer('Отправить пост?', reply_markup=send_post_kb(message))
    post_chat_message = PostInfoData(original_message_id=message.message_id,
                                     copied_message_id=copied_message.message_id,
                                     manage_message_id=manage_message.message_id,
                                     manage_chat_id=message.chat.id,
                                     channel_id=-1002035366472, publication_at=int(time.time() + 600),
                                     delete_at=None, status=PostStatus.NEW)

    # сохраняем информацию об управляющем посте в storage
    store = PostsStoreHandler()
    await store.set_data(post_chat_message)

    await state.clear()


@posts_router.callback_query(SendPostNowCallback.filter())
async def send_now(query: CallbackQuery, callback_data: SendPostNowCallback, bot: Bot):
    """ Нажата кнопка 'Отправить сразу' """
    await bot.copy_message(chat_id='-1002035366472', from_chat_id=callback_data.chat_id,
                           message_id=callback_data.message_id)
    store = PostsStoreHandler()

    await store.update_status(callback_data.message_id, callback_data.chat_id, PostStatus.SENT)
    await query.answer()


@posts_router.callback_query(SendPostDelayCallback.filter())
async def send_delay(query: CallbackQuery, callback_data: SendPostDelayCallback, bot: Bot, state: FSMContext):
    """ Нажата кнопка 'Отправить с задержкой' """
    # await bot.send_message(chat_id=callback_data.chat_id, reply_markup=await SimpleCalendar().start_calendar(),
    #                        text='Выбери дату')
    await state.set_state(CreatePostFSM.date_pick)
    await query.answer()
