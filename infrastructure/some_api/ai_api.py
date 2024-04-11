from dataclasses import dataclass
from enum import Enum

from infrastructure.some_api.base import BaseClient
from infrastructure.some_api.exception import ApiHttpException
from infrastructure.some_api.type import ApiResponseType
from tgbot.config import load_config


@dataclass
class AiRequestCompletionOptions:
    stream: bool  # Enables streaming of partially generated text.
    temperature: float  # Affects creativity and randomness of responses. Should be a double number between 0
    # (inclusive) and 1 (inclusive).
    maxTokens: int  # The limit on the number of tokens used for single completion generation. Must be greater than zero


class Role(Enum):
    SYSTEM = "system"  # special role used to define the behaviour of the completion model
    ASSISTANT = "assistant"  # a role used by the model to generate responses
    USER = "user"  # a role used by the user to describe requests to the model


@dataclass
class AiMessage:
    role: Role  # Identifier of the message sender.
    text: str  # Textual content of the message.


@dataclass
class AiRequest:
    modelUri: str  # The identifier of the model to be used for completion generation.
    completionOptions: AiRequestCompletionOptions  # Configuration options for completion generation.
    messages: list[AiMessage]


@dataclass
class AiResponseAlternatives:
    message: AiMessage
    status: str


@dataclass
class AiResponseUsage:
    inputTextTokens: str
    completionTokens: str
    totalTokens: str


@dataclass
class AiResponse:
    alternatives: list[AiResponseAlternatives]
    usage: AiResponseUsage
    modelVersion: str


config = load_config()


class YandexChatGpt(BaseClient):
    def __init__(self):
        self.api_key = config.gpt.api_key
        super().__init__(base_url=config.gpt.service_url)

    async def _get_request(self, params: dict) -> ApiResponseType:
        headers = {'Accept': 'application/json', 'Authorization': f'Api-Key {self.api_key}'}
        result = await self._make_request(url='/foundationModels/v1/completion', method="POST",
                                          headers=headers, json=params)
        return result

    async def do_request(self, request: AiRequest):
        params = self._request_transform(request)
        code, result = await self._get_request(params)
        await self.close()
        if code == 200:
            return self._response_parse(result['result'])
        raise ApiHttpException(f'Ошибка ответа от Яндекс GPT, код: {code}')

    def _request_transform(self, request: AiRequest) -> dict:
        return {
            "modelUri": request.modelUri,
            "completionOptions": {
                "stream": request.completionOptions.stream,
                "temperature": request.completionOptions.temperature,
                "maxTokens": request.completionOptions.maxTokens
            },
            "messages": [{'role': i.role.value, 'text': i.text} for i in request.messages]
        }

    def _response_parse(self, response: dict) -> AiResponse:
        alternatives = [AiResponseAlternatives(status=i['status'],
                                               message=AiMessage(text=i['message']['text'],
                                                                 role=Role[i['message']['role'].upper()])) for i in
                        response['alternatives']]
        usage = AiResponseUsage(inputTextTokens=response['usage']['inputTextTokens'],
                                completionTokens=response['usage']['completionTokens'],
                                totalTokens=response['usage']['totalTokens'])
        result = AiResponse(modelVersion=response['modelVersion'], alternatives=alternatives, usage=usage)
        return result
