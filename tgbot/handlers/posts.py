import time
from datetime import datetime

from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

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
    manage_message = await message.answer('Отправить пост?', reply_markup=send_post_kb(message,
                                                                                       original_message_id=copied_message.message_id))
    post_chat_message = PostInfoData(original_message_id=copied_message.message_id,
                                     manage_message_id=manage_message.message_id,
                                     manage_chat_id=message.chat.id,
                                     channel_id=-1002035366472,
                                     status=PostStatus.NEW)

    # сохраняем информацию об управляющем посте в storage
    store = PostsStoreHandler()
    await store.set_data(post_chat_message)

    await state.clear()


@posts_router.callback_query(SendPostNowCallback.filter())
async def send_now(query: CallbackQuery, callback_data: SendPostNowCallback, bot: Bot):
    """ Нажата кнопка 'Отправить сразу' """
    copied_message = await bot.copy_message(chat_id='-1002035366472', from_chat_id=callback_data.chat_id,
                                            message_id=callback_data.original_message_id)
    store = PostsStoreHandler()
    data = PostInfoData(original_message_id=callback_data.original_message_id,
                        copied_message_id=copied_message.message_id,
                        manage_message_id=callback_data.manage_message_id,
                        manage_chat_id=callback_data.manage_chat_id,
                        channel_id=-1002035366472,
                        publication_at=int(time.time()),
                        status=PostStatus.SENT)
    await store.set_data(data)

    await store.update_status(callback_data.original_message_id, callback_data.chat_id, PostStatus.SENT)
    await query.answer()


@posts_router.callback_query(SendPostDelayCallback.filter())
async def send_delay(query: CallbackQuery, callback_data: SendPostDelayCallback, bot: Bot, state: FSMContext):
    """ Нажата кнопка 'Отправить с задержкой' """
    await bot.send_message(chat_id=callback_data.chat_id, reply_markup=await SimpleCalendar().start_calendar(),
                           text='Выбери дату')
    await state.set_state(CreatePostFSM.date_pick)
    data = {
        "original_message_id": callback_data.original_message_id,
        "manage_chat_id": callback_data.manage_chat_id,
        "channel_id": -1002035366472
    }
    await state.set_data(data)
    await query.answer()


@posts_router.callback_query(SimpleCalendarCallback.filter())
async def set_date_delay(query: CallbackQuery, callback_data: SimpleCalendarCallback, bot: Bot, state: FSMContext):
    """ Обработка коллбэка установки даты """
    # получаем состояние из FSM
    state_data = await state.get_data()
    original_message_id = state_data.get('original_message_id')
    manage_chat_id = state_data.get('manage_chat_id')
    # получаем данные из БД
    store = PostsStoreHandler()
    store_data = await store.get_data(original_message_id=original_message_id, manage_chat_id=manage_chat_id)

    await bot.send_message(chat_id=state_data.get('manage_chat_id'),
                           text='Напиши время публикации в формате 17:24')
    # собираем дату из колбэка
    date_string=f'{callback_data.year}-{callback_data.month}-{callback_data.day}'
    date_format = "%Y-%m-%d"
    timestamp = datetime.strptime(date_string, date_format).timestamp()
    update_data = PostInfoData(original_message_id=store_data.get('original_message_id'),
                               manage_message_id=store_data.get('manage_message_id'),
                               manage_chat_id=store_data.get('manage_chat_id'),
                               channel_id=store_data.get('channel_id'),
                               publication_at=int(timestamp),
                               status=PostStatus.DELAYED)
    await store.set_data(update_data)
    await state.set_state(CreatePostFSM.date_pick)
    # удаляем сообщение с выбором даты
    await query.message.delete()


@posts_router.message(StateFilter(CreatePostFSM.time_pick))
async def new_post(message: Message, state: FSMContext):
    """ Получено время публикации """
    await message.answer(text='Заявка на публикацию принята')
    await state.clear()
