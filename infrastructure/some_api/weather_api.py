from dataclasses import dataclass
from typing import Any

from infrastructure.some_api.base import BaseClient
from tgbot.config import load_config
from .coordinate_dto import Coordinate
from .exception import ApiHttpException
from .type import ApiResponseType

config = load_config()


@dataclass
class WeatherDto:
    fact_temp: int
    fact_feels_like: int
    fact_condition: str
    url: str


class YaWeatherApi(BaseClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weather.yandex.ru"
        super().__init__(base_url=self.base_url)

    async def _get_request(self, coordinate: Coordinate) -> tuple[int, dict[str, Any]]:
        headers = {'X-Yandex-API-Key': self.api_key, 'Accept': 'application/json'}

        params = {'lat': str(coordinate.latitude), 'lon': str(coordinate.longitude)}
        if config.weather and config.weather.lang:
            params['lang'] = config.weather.lang
        result = await self._make_request(url='/v2/informers', method="GET", headers=headers, params=params)

        return result

    async def get_weather(self, coordinate: Coordinate) -> WeatherDto:
        result = await self._get_request(coordinate)
        await self.close()
        return self.parsing_result(result)

    def parsing_result(self, result: ApiResponseType) -> WeatherDto:
        if result[0] == 200:
            fact = result[1]['fact']
            info = result[1]['info']

            return WeatherDto(fact_temp=fact['temp'], fact_feels_like=fact['feels_like'],
                              fact_condition=fact['condition'], url=info['url'])
        else:
            raise ApiHttpException(f'Ошибка ответа от Яндекс погоды, код: {result[0]}')
