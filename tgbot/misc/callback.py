from aiogram.filters.callback_data import CallbackData


class ProfileNameCallback(CallbackData, prefix="profile"):
    action: str
    chat_id: int
    user_id: int


class SendPostNowCallback(CallbackData, prefix="send_now"):
    action: str
    chat_id: int
    original_message_id: int
    manage_message_id: int
    manage_chat_id: int


class SendPostDelayCallback(CallbackData, prefix='send_delay'):
    action: str
    chat_id: int
    original_message_id: int
    manage_message_id: int
    manage_chat_id: int