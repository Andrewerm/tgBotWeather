import asyncio
import json
import logging

import betterlogging as bl  # type: ignore
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.misc.commands_menu import set_main_menu
from tgbot.services.logging_config import YcLoggingFormatter
from tgbot.services.posts_data_store import PostsStoreHandler, PostStatus
from ydb_storage.storage import YDBDocumentStorage, YDBStorage


def get_storage(config) -> BaseStorage:
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """
    if config.tg_bot.storage == 'redis':
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    elif config.tg_bot.storage == 'yadb_document':
        return YDBDocumentStorage()
    elif config.tg_bot.storage == 'yadb_table':
        return YDBStorage(driver_config=config.yadb.db_config, serializing_method='json')
    else:
        return MemoryStorage()


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        # DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def start_script():
    config = load_config()
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    if config.misc.app_env == 'yandex':
        handler.setFormatter(YcLoggingFormatter('%(message)s %(level)s %(logger)s'))
    if config.misc.app_env == 'local':
        handler.setFormatter(bl.ColorizedFormatter(hide_lib_diagnose=False))
    root_logger.addHandler(handler)
    root_logger.propagate = False
    root_logger.setLevel(logging.DEBUG)
    storage = get_storage(config)
    dp_instance = Dispatcher(storage=storage)
    dp_instance.include_routers(*routers_list)
    bot_instance = Bot(token=config.tg_bot.token)
    register_global_middlewares(dp_instance, config)
    return dp_instance, bot_instance


# Инициализация диспетчера и бота и логирования
dp, bot = start_script()


async def main():
    await set_main_menu(bot)
    await bot.delete_webhook()
    await dp.start_polling(bot)


async def ya_handler(event, context) -> dict:
    await set_main_menu(bot)
    tg_context: str = event['body']
    tg_context_dict = json.loads(tg_context)
    await dp.feed_raw_update(bot=bot, update=tg_context_dict)

    return {
        'statusCode': 200,
    }

async def delayed_task_exec() -> dict:
    """ Выполнение задач по отложенной публикации и удалению """
    store = PostsStoreHandler()
    try:
        results = await store.exec_get_delayed_list()
        for item in results:
            copied_message = await bot.copy_message(chat_id='-1002035366472', from_chat_id=item['manage_chat_id'],
                                                    message_id=item['original_message_id'])
            store = PostsStoreHandler()

            await store.update_status(item['original_message_id'], item['manage_chat_id'], PostStatus.SENT)

        statusCode = 200
        logging.debug(f'Событие по таймеру, исполнено: {results} событий')
    except Exception as e:
        statusCode = 500
        logging.error(e)

    return {
        'statusCode': statusCode,
    }


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот остановлен!")
