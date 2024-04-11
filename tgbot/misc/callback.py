from aiogram.filters.callback_data import CallbackData


class ProfileNameCallback(CallbackData, prefix="profile"):
    action: str
    chat_id: int
    user_id: int
