from typing import Optional

from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.misc.callback import SendPostNowCallback, SendPostDelayCallback


def send_post_kb(message: Message) -> Optional[InlineKeyboardMarkup]:
    if message.from_user:
        keyboard = InlineKeyboardBuilder()

        keyboard.button(
            text="📤 Отправить сразу",
            callback_data=SendPostNowCallback(action='send',
                                              chat_id=message.chat.id,
                                              user_id=message.from_user.id,
                                              message_id=message.message_id).pack()
        )
        keyboard.button(
            text="⏳ отправить с задержкой",
            callback_data=SendPostDelayCallback(action='delay',
                                                chat_id=message.chat.id,
                                                message_id=message.message_id
                                                ).pack()
        )

        # If needed you can use keyboard.adjust() method to change the number of buttons per row
        # keyboard.adjust(2)

        # Then you should always call keyboard.as_markup() method to get a valid InlineKeyboardMarkup object
        return keyboard.as_markup()
    else:
        return None
