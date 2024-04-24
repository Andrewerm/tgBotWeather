import pytest
from ydb import table

from tgbot import config
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
async def test_ya_db():
        endpoint = 'grpcs://ydb.serverless.yandexcloud.net:2135'
        database = 'your_database'
        table_name = 'your_table'

        driver_config = table.DriverConfig(endpoint=endpoint)
        driver = table.Driver(driver_config)

        async with driver.table_client(database=database, table=table_name) as client:
            # Создание структуры записи
            record_scheme = Record(
                "key", Utf8(),
                "value", Decimal()
            )

            # Вставка документа
            await client.upsert(
                record_scheme,
                {
                    "key": "document_key",
                    "value": 123.45
                }
            )

            print("Документ успешно вставлен")