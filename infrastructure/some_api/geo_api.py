from dataclasses import dataclass
from typing import Optional

from infrastructure.some_api.base import BaseClient
from infrastructure.some_api.exception import ApiParsingException, ApiHttpException
from infrastructure.some_api.type import ApiResponseType
from infrastructure.some_api.weather_api import Coordinate
from tgbot.config import load_config

config = load_config()


@dataclass
class YaGeoDto:
    name: str
    description: str
    geo: Optional[Coordinate] = None


class YaGeoApi(BaseClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://geocode-maps.yandex.ru"
        super().__init__(base_url=self.base_url)

    async def _get_request(self, coordinate: Coordinate) -> ApiResponseType:
        headers = {'Accept': 'application/json'}
        params = {'geocode': str(coordinate.longitude) + ',' + str(coordinate.latitude),
                  'apikey': self.api_key,
                  'format': 'json',
                  'results': '1',
                  'kind': 'locality'}
        if config.geo and config.geo.lang:
            params['lang'] = config.geo.lang
        result = await self._make_request(url='/1.x/', method="GET", headers=headers, params=params)

        return result

    async def get_geo(self, coordinate: Coordinate) -> YaGeoDto:
        result = await self._get_request(coordinate)
        await self.close()
        return self.parsing_result(result)

    def parsing_result(self, result: ApiResponseType) -> YaGeoDto:
        if result[0] == 200:
            try:
                response = result[1]['response']
                geo_object_collection = response['GeoObjectCollection']
                feature_member = geo_object_collection['featureMember']
                if len(feature_member):
                    geo_object = feature_member[0]['GeoObject']
                    name = geo_object['name']
                    description = geo_object['description']
                    geo = geo_object['Point']['pos']
                    [long, lat] = geo.split(' ')
                    coordinate = Coordinate(latitude=lat, longitude=long)
                    return YaGeoDto(name=name, description=description, geo=coordinate)
                else:
                    return YaGeoDto(name='не известно', description='')
            except KeyError as err:
                raise ApiParsingException(f'Ошибка парсинга {err}')

        else:
            raise ApiHttpException(f'Ошибка ответа от Яндекс геокодирования, код: {result[0]}')
