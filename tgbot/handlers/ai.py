from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from infrastructure.some_api.ai_api import AiRequestCompletionOptions, AiMessage, Role, AiRequest, YandexChatGpt
from tgbot import config

ai_router = Router()
ai_router.message.filter(F.text.startswith('Петя'))


@ai_router.message(F.text)
async def promt_ai(message: Message, state: FSMContext):
    user_data: dict = await state.get_data()
    # получаем имя пользователя, если есть
    user_name = user_data.get('profile_name', '')
    user_position = user_data.get('profile_profession', '')
    conf = config.load_config()
    lenRobot = len('Петя')+1
    completionOptions = AiRequestCompletionOptions(stream=False, maxTokens=2000, temperature=0.5)
    messageSystem = AiMessage(role=Role.SYSTEM, text=f'Тебя спрашивает человек по имени: {user_name}, '
                                                     f'род занятия которого: {user_position}. '
                                                     f'Обратись к нему по имени и ответь на вопрос')
    messagesUser = AiMessage(role=Role.USER, text=message.text[lenRobot:])
    ai_request = AiRequest(modelUri=conf.gpt.gpt_lite_uri, completionOptions=completionOptions,
                           messages=[messagesUser, messageSystem])
    ai_service = YandexChatGpt()
    result = await ai_service.do_request(ai_request)
    await message.reply(result.alternatives[0].message.text)
