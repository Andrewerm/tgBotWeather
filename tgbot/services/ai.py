from typing import Optional, Any

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from infrastructure.some_api.ai_api import AiRequest, AiMessage, Role, AiRequestCompletionOptions, \
    AiResponseAlternatives
from tgbot import config
from tgbot.misc.profile import ProfileDictEnum

conf = config.load_config()


class AiRequestBuilder:
    _request: str
    _ai_request: AiRequest
    _state: FSMContext
    _message: Message
    _user_data: Optional[dict[str, Any]] = None
    _system_role_message: AiMessage

    def __init__(self, state: FSMContext, message: Message):
        self._config = config.load_config()
        self._state = state
        self._message = message
        completionOptions = AiRequestCompletionOptions(stream=False, maxTokens=2000, temperature=0.9)
        # messageBuild = [messageSystem] + content if content else [messageSystem]
        self._ai_request = AiRequest(modelUri=conf.gpt.gpt_lite_uri, completionOptions=completionOptions,
                                     messages=[])

    async def _get_user_data(self) -> Optional[dict[str, Any]]:
        if self._user_data:
            return self._user_data
        else:
            data = await self._state.get_data()
            if data:
                self._user_data = data
            return data

    async def set_system_role(self) -> None:
        self._request = ''
        self._add_start_instructions()
        user_data = await self._get_user_data()
        if user_data:
            user_nick = user_data.get(ProfileDictEnum.NICK.value)
            nick = user_nick if user_nick else self._message.from_user.first_name if self._message.from_user else None
            user_position = user_data.get(ProfileDictEnum.POSITION.value)
            if nick:
                self._add_asker_name(nick)
            if user_position:
                self._add_asker_position(user_position)
        self._bot_role()
        self._add_finish_instructions()
        self._system_role_message = AiMessage(role=Role.SYSTEM, text=self._request)

    def _add_start_instructions(self) -> None:
        self._request += f'Мы с тобой делаем собеседника для общения в телеграмм. \n'
        'Твои ответы должны быть максимально похожи на разговорную речь.\n'

    def _bot_role(self) -> None:
        self._request += f'Ты человек, который долго сидел в  тюрьме с соответствующим словарным запасом и сленгом.\n'

    def _add_finish_instructions(self) -> None:
        self._request += f'Ответ напиши от своего имени без тире в начале и только прямую речь.\n'
        'Ответ должен содержать не менее 600 символов.\n'

    def _add_asker_name(self, name: Optional[str]) -> None:
        if name:
            self._request += f'Тебе задаёт вопрос человек по имени {name}. '

    def _add_asker_position(self, position: Optional[str]):
        if position:
            self._request += f'Задающиё вопрос по роду занятий: {position}.'

    def _add_bot_names(self) -> None:
        self._request += f'Твои имена: {", ".join(self._config.tg_bot.bot_names)}. '

    def get_result(self) -> AiRequest:
        self._ai_request.messages = [self._system_role_message]
        return self._ai_request


async def get_chat_content(state: FSMContext):
    user_data = await state.get_data()
    content = user_data.get(ProfileDictEnum.CHAT_HISTORY.value, '') if user_data else None


async def chat_preparing(state: FSMContext, message: Message) -> AiRequest:
    user_data = await state.get_data()
    nick, user_position, content = None, None, None
    if user_data:
        user_nick = user_data.get(ProfileDictEnum.NICK.value)
        nick = user_nick if user_nick else message.from_user.first_name if message.from_user else None
        user_position = user_data.get(ProfileDictEnum.POSITION.value)
        content: Optional[list[AiMessage]] = user_data.get(ProfileDictEnum.CHAT_HISTORY.value)  # type: ignore

    # if user_position:
    #     setAnswer = f'{setAnswer}Его профессия: {user_position}. '
    # setAnswer = (f'{setAnswer} Ответь его на вопрос прямой речью в стиле человека, который просидел много лет в '
    #              f'тюрьме. Дай только один вариант ответа.')
    # messageSystem = AiMessage(role=Role.SYSTEM, text=setAnswer)
    completionOptions = AiRequestCompletionOptions(stream=False, maxTokens=2000, temperature=0.9)
    # messageBuild = [messageSystem] + content if content else [messageSystem]
    # request = AiRequest(modelUri=conf.gpt.gpt_lite_uri, completionOptions=completionOptions,
    #                     messages=messageBuild)

    # return request


def chat_add_request(request: AiRequest, new_message: AiMessage) -> AiRequest:
    request.messages.append(new_message)
    return request


async def save_chat_history(request: AiRequest, answer: AiResponseAlternatives, state: FSMContext) -> None:
    request.messages.append(answer.message)
    without_system = list(filter(lambda x: x.role != Role.SYSTEM, request.messages))
    await state.update_data({ProfileDictEnum.CHAT_HISTORY.value: without_system})
