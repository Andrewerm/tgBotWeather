from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from infrastructure.some_api.ai_api import YandexChatGpt
from tgbot.filters.bot_name import BotNameFilter, IsNotGroup
from tgbot.services import ai
from tgbot.services.ai import AiRequestBuilder

ai_router = Router()


# ai_router.message.filter(IsNotGroup())


@ai_router.message(F.text, IsNotGroup())
@ai_router.message(F.text, BotNameFilter())
async def promt_ai(message: Message, state: FSMContext) -> None:
    if message.text:
        builder = AiRequestBuilder(state, message)

        # user_data = await state.get_data()
        # user_position = user_data.get(ProfileDictEnum.POSITION.value, '') if user_data else None
        # user_chat_content=user_data.get(ProfileDictEnum.CHAT_HISTORY.value, '') if user_data else None
        # conf = config.load_config()
        # completionOptions = AiRequestCompletionOptions(stream=False, maxTokens=2000, temperature=0.9)

        # messageSystem = AiMessage(role=Role.SYSTEM, text=setAnswer)

        # messagesUser = AiMessage(role=Role.USER, text=message.text + '?')
        # ai_request = AiRequest(modelUri=conf.gpt.gpt_lite_uri, completionOptions=completionOptions,
        #                        messages=[messagesUser, messageSystem])

        await builder.set_system_role()
        requestMessage = builder.get_result()
        # ai_request = await ai.chat_preparing(state, message)
        # ai_request_new = ai.chat_add_request(ai_request, requestMessage)
        yandex_ai_service = YandexChatGpt()
        result = await yandex_ai_service.do_request(requestMessage)
        await ai.save_chat_history(requestMessage, result.alternatives[0], state)
        await message.reply(result.alternatives[0].message.text)
