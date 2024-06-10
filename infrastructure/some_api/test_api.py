import pytest

from tgbot import config
from tgbot.services.posts_data_store import PostsStoreHandler, PostInfo
from .ai_api import AiRequest, AiRequestCompletionOptions, AiMessage, Role, YandexChatGpt, AiResponse
from .geo_api import YaGeoDto, YaGeoApi
from .weather_api import YaWeatherApi, Coordinate, WeatherDto


@pytest.mark.asyncio
async def test_ya_weather_api():
    conf = config.load_config()
    coord = Coordinate(longitude=0, latitude=0)
    weather_service = YaWeatherApi(api_key=conf.weather.api_key)
    result = await weather_service.get_weather(coord)
    assert isinstance(result, WeatherDto)


@pytest.mark.asyncio
async def test_ya_geo_api():
    conf = config.load_config()
    coord = Coordinate(longitude=55.859549, latitude=49.086678)
    geo_service = YaGeoApi(api_key=conf.geo.api_key)
    result = await geo_service.get_geo(coord)
    assert isinstance(result, YaGeoDto)


@pytest.mark.asyncio
async def test_ya_gpt():
    conf = config.load_config()
    completionOptions = AiRequestCompletionOptions(stream=False, maxTokens=2000, temperature=0)
    messageSystem = AiMessage(role=Role.SYSTEM, text='Ты учитель литературы')
    messagesUser = AiMessage(role=Role.USER, text='Расскажи чем между собой похожи братья Карамазовы')
    ai_request = AiRequest(modelUri=conf.gpt.gpt_lite_uri, completionOptions=completionOptions,
                           messages=[messagesUser, messageSystem])
    ai_service = YandexChatGpt()
    result = await ai_service.do_request(ai_request)
    assert isinstance(result, AiResponse)


@pytest.mark.asyncio
async def test_save_ya_db():
    # post_chat_message = PostInfo(post_message_id=1, manage_message_id=1,
    #                              manage_chat_id=1,
    #                              channel_id=1002035366472)
    service = PostsStoreHandler()
    await service.set_data()
    await service.stop_driver()


@pytest.mark.asyncio
async def test_read_ya_db():
    service = PostsStoreHandler()
    res = await service.get_data()
    print(res)
    await service.stop_driver()


@pytest.mark.asyncio
async def test_create_table():
    service = PostsStoreHandler()
    await service.create_table()
    await service.stop_driver()


@pytest.mark.asyncio
async def test_delete_table():
    service = PostsStoreHandler()
    await service.delete_table()
    await service.stop_driver()
