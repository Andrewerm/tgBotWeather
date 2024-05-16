from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from infrastructure.some_api.ai_api import YandexChatGpt
from tgbot.filters.bot_name import BotNameFilter, IsNotGroup
from tgbot.services.ai import AiRequestBuilder

ai_router = Router()


# ai_router.message.filter(IsNotGroup())


@ai_router.message(F.text, IsNotGroup())
@ai_router.message(F.text, BotNameFilter())
async def promt_ai(message: Message, state: FSMContext) -> None:
    if message.text:
        builder = AiRequestBuilder(state, message)

        # получение подготовленного запроса
        requestMessage = await builder.get_ai_request()

        # запрос в GPT
        yandex_ai_service = YandexChatGpt()
        result = await yandex_ai_service.do_request(requestMessage)
        # сохранение ответа в историю
        requestMessage.messages.append(result.alternatives[0].message)

        # сохранение истории чата в storage
        await builder.save_history_to_storage()

        # requestMessage.messages.append(AiMessage(text=result.alternatives[0], role=Role.USER))
        await message.reply(result.alternatives[0].message.text)
