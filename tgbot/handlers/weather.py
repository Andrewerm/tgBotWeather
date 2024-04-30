import json

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from infrastructure.some_api.geo_api import YaGeoApi, YaGeoDto
from infrastructure.some_api.weather_api import YaWeatherApi, Coordinate, WeatherDto
from tgbot.config import load_config

weather_router = Router()

config = load_config()


async def get_weather_data(coordinate: Coordinate) -> tuple[WeatherDto, YaGeoDto]:
    if not config.weather or not config.geo:
        raise Exception
    weather_service = YaWeatherApi(api_key=config.weather.api_key)
    geo_service = YaGeoApi(api_key=config.geo.api_key)
    weather_data = await weather_service.get_weather(coordinate)
    defined_location = await geo_service.get_geo(coordinate)
    return weather_data, defined_location


@weather_router.message(F.location)
async def location_weather(message: Message, state: FSMContext):
    if message and message.location and config.geo and config.weather:
        location = message.location
        coordinates = Coordinate(longitude=location.longitude, latitude=location.latitude)
        # Сериализация объекта в строку
        serialized_coordinate = json.dumps(coordinates.__dict__)
        # сохраняем данные сессии пользователя
        await state.update_data({'coordinates': serialized_coordinate})
        await get_weather_location(message, state)


@weather_router.message(Command('weather'))
async def get_weather_location(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data and message and user_data.get('coordinates'):
        coordinates: str = user_data['coordinates']
        # Десериализация строки обратно в объект
        deserialized_dto: dict = json.loads(coordinates)
        coord_dto = Coordinate(latitude=deserialized_dto['latitude'], longitude=deserialized_dto['longitude'])
        [weather_data, defined_location] = await get_weather_data(coord_dto)

        # Создаем объект InlineKeyboardButton
        button_details = InlineKeyboardButton(text="Подробности", url=weather_data.url)

        # Создаем объект InlineKeyboardMarkup и добавляем кнопку
        markup = InlineKeyboardMarkup(inline_keyboard=[[button_details]])
        await message.reply(
            f"🧭 {message.from_user.first_name}, ты находишься: {defined_location.description}, {defined_location.name} \n"
            f"Погода на текущий момент:\n"
            f"🌡️ фактическая температура: {weather_data.fact_temp},\n"
            f"🐱 по ощущению: {weather_data.fact_feels_like},\n"
            f"☀️ условия: {weather_data.fact_condition}\n",
            reply_markup=markup)
    else:
        await message.reply(f"Сначала сообщи своё местоположение, {message.from_user.first_name}")
