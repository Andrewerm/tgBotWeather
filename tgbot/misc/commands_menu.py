from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Познакомиться'),
        BotCommand(command='/weather',
                   description='Узнать погоду'),
        BotCommand(command='/posts',
                   description='Работа с постами'),
    ]

    await bot.set_my_commands(main_menu_commands)
