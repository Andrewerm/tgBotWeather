from typing import Optional

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.misc.callback import ProfileNameCallback


def keyboard_cancel(message: Message) -> Optional[InlineKeyboardMarkup]:
    if message.from_user:
        button = InlineKeyboardButton(text='Не хочу отвечать',
                                      callback_data=ProfileNameCallback(action='cancel_name',
                                                                        chat_id=message.chat.id,
                                                                        user_id=message.from_user.id).pack())
        markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
        return markup
    else:
        return None
