from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from infrastructure.some_api.ai_api import AiRequestCompletionOptions, AiMessage, Role, AiRequest, YandexChatGpt
from tgbot import config
from tgbot.filters.bot_name import BotNameFilter, IsNotGroup

ai_router = Router()


# ai_router.message.filter(IsNotGroup())


@ai_router.message(F.text, IsNotGroup())
@ai_router.message(F.text, BotNameFilter())
async def promt_ai(message: Message, state: FSMContext) -> None:
    if message.text:
        user_data = await state.get_data()
        user_position = user_data.get('profile_profession', '') if user_data else None
        conf = config.load_config()
        completionOptions = AiRequestCompletionOptions(stream=False, maxTokens=2000, temperature=0.9)
        setAnswer = f'Твои имена: {", ".join(conf.tg_bot.bot_names)}. Тебе задаёт вопрос человек по имени {message.from_user.first_name}. '  # type: ignore
        if user_position:
            setAnswer = f'{setAnswer}Его профессия: {user_position}. '
        setAnswer = (f'{setAnswer} Ответь его на вопрос прямой речью в стиле человека, который просидел много лет в '
                     f'тюрьме. Дай только один вариант ответа.')

        messageSystem = AiMessage(role=Role.SYSTEM, text=setAnswer)

        messagesUser = AiMessage(role=Role.USER, text=message.text + '?')
        ai_request = AiRequest(modelUri=conf.gpt.gpt_lite_uri, completionOptions=completionOptions,
                               messages=[messagesUser, messageSystem])
        ai_service = YandexChatGpt()
        result = await ai_service.do_request(ai_request)
        await message.reply(result.alternatives[0].message.text)
