import pytest

from tgbot import config
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
