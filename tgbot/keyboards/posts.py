from typing import Optional

from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.misc.callback import SendPostNowCallback, SendPostDelayCallback


def send_post_kb(message: Message, original_message_id: int) -> Optional[InlineKeyboardMarkup]:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="📤 Отправить сразу",
        callback_data=SendPostNowCallback(action='send',
                                          original_message_id=original_message_id,
                                          chat_id=message.chat.id,
                                          manage_message_id=message.message_id,
                                          manage_chat_id=message.chat.id
                                          ).pack()
    )
    keyboard.button(
        text="⏳ отправить с задержкой",
        callback_data=SendPostDelayCallback(action='delay',
                                            original_message_id=original_message_id,
                                            chat_id=message.chat.id,
                                            manage_message_id=message.message_id,
                                            manage_chat_id=message.chat.id
                                            ).pack()
    )

    # If needed you can use keyboard.adjust() method to change the number of buttons per row
    # keyboard.adjust(2)

    # Then you should always call keyboard.as_markup() method to get a valid InlineKeyboardMarkup object
    return keyboard.as_markup()
