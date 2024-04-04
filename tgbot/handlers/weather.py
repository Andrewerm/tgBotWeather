from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from infrastructure.some_api.geo_api import YaGeoApi, YaGeoDto
from infrastructure.some_api.weather_api import YaWeatherApi, Coordinate, WeatherDto
from tgbot.config import load_config

weather_router = Router()

config = load_config()


class PersonState(StatesGroup):
    location_set = State()


# @weather_router.message(Command('weather'))
# async def ask_weather(message: Message):
#     await message.reply('Вам погоду?', reply_markup=select_day_kb())


@weather_router.callback_query(F.data.in_({'today', 'tomorrow'}))
async def today_weather(callback: CallbackQuery):
    if callback and callback.data and isinstance(callback.message, Message):
        variants = {'today': 'сегодня', 'tomorrow': 'завтра'}
        result = variants[callback.data]
        await callback.message.answer(f'Погода {result}')
        await callback.answer()


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
        [weather_data, defined_location] = await get_weather_data(coordinates)

        # Создаем объект InlineKeyboardButton
        button = InlineKeyboardButton(text="Подробности", url=weather_data.url)

        # Создаем объект InlineKeyboardMarkup и добавляем кнопку
        markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
        await message.reply(
            f"🧭 Ваше местоположение: {defined_location.description}, {defined_location.name}\n"
            f"Погода:\n"
            f"🌡️ фактическая температура: {weather_data.fact_temp},\n"
            f"🐱 по ощущению: {weather_data.fact_feels_like},\n"
            f"☀️ условия: {weather_data.fact_condition}\n",
            reply_markup=markup)
        await state.set_state(PersonState.location_set)
        await state.set_data({'coordinates': coordinates})


@weather_router.message(Command('weather'), StateFilter(None))
async def get_weather_no_location(message: Message):
    await message.reply('Сначала сообщи своё местоположение')


@weather_router.message(Command('weather'), StateFilter(PersonState.location_set))
async def get_weather_location(message: Message, state: FSMContext):
    user_data = await state.get_data()
    coordinates = user_data['coordinates']
    [weather_data, defined_location] = await get_weather_data(coordinates)

    # Создаем объект InlineKeyboardButton
    button_details = InlineKeyboardButton(text="Подробности", url=weather_data.url)
    button_change_location = InlineKeyboardButton(text='Сменить локацию', callback_data='change_location')

    # Создаем объект InlineKeyboardMarkup и добавляем кнопку
    markup = InlineKeyboardMarkup(inline_keyboard=[[button_details, button_change_location]])
    await message.reply(
        f"🧭 Ваше местоположение: {defined_location.description}, {defined_location.name}"
        f"Погода:\n"
        f"🌡️ фактическая температура: {weather_data.fact_temp},\n"
        f"🐱 по ощущению: {weather_data.fact_feels_like},\n"
        f"☀️ условия: {weather_data.fact_condition}\n",
        reply_markup=markup)
    await state.set_state(PersonState.location_set)
    await state.set_data({'coordinates': coordinates})
