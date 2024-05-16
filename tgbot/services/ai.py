from typing import Optional, Any

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from infrastructure.some_api.ai_api import AiRequest, AiMessage, Role, AiRequestCompletionOptions
from tgbot import config
from tgbot.misc.profile import ProfileDictEnum

conf = config.load_config()


class AiRequestBuilder:
    _request: str
    _ai_request: AiRequest
    _state: FSMContext
    _message: Message
    _user_question: str
    _user_data: Optional[dict[str, Any]] = None
    _system_role_message: AiMessage
    _chat_history: list[dict[str, str]] = []

    def __init__(self, state: FSMContext, message: Message):
        self._config = config.load_config()
        self._state = state
        self._message = message
        if message.text:
            self._user_question = message.text
        completionOptions = AiRequestCompletionOptions(stream=False, maxTokens=2000, temperature=0.7)
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

    async def restore_history_chat(self) -> None:
        user_data = await self._get_user_data()
        if user_data and (history := user_data.get(ProfileDictEnum.CHAT_HISTORY.value)):
            self._ai_request.messages = [AiMessage(role=Role(key), text=value) for item in history for key, value in
                                         item.items()]
        self._ai_request.messages.append(AiMessage(role=Role.USER, text=self._user_question))

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
            self._request += f'Задающий вопрос имеет род занятий: {position}.'

    def _add_bot_names(self) -> None:
        self._request += f'Твои имена: {", ".join(self._config.tg_bot.bot_names)}. '

    async def get_ai_request(self) -> AiRequest:
        # восстановление истории чата
        await self.restore_history_chat()
        # установка системной роли
        await self.set_system_role()
        # вставляем системную роль
        self._ai_request.messages.insert(0, self._system_role_message)

        return self._ai_request

    async def save_history_to_storage(self):
        """ Сохранение контекста общения с ботом """
        # убираем системную роль
        without_system = list(filter(lambda x: x.role != Role.SYSTEM, self._ai_request.messages))
        # отрезаем сообщения, которые старше заданной глубины
        count_messages = len(without_system)
        cut_old_messages = without_system[
                           -self._config.tg_bot.gpt_context_deep * 2:] if count_messages > self._config.tg_bot.gpt_context_deep * 2 else without_system
        dict_prepare = [{x.role.value: x.text} for x in cut_old_messages]
        await self._state.update_data({ProfileDictEnum.CHAT_HISTORY.value: dict_prepare})
