from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot.config import Config


def contains_substring(text, substrings):
    for substring in substrings:
        if substring in text:
            return True
    return False


class BotNameFilter(BaseFilter):
    """ Проверяет что было обращение по имени бота """

    async def __call__(self, message: Message, config: Config) -> bool:

        if message and message.text:
            names = config.tg_bot.bot_names
            if contains_substring(message.text, names):
                return True

        return False


class IsNotGroup(BaseFilter):
    """ Проверяет что это не группа """

    async def __call__(self, message: Message) -> bool:
        return message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]
