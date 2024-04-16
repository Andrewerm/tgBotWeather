import logging
import os
from aiogram import Bot


def init_environment() -> dict:
    bot_token = os.getenv('BOT_TOKEN')
    webhook_url = os.getenv('WEBHOOK_URL')
    webhook_path = os.getenv('WEBHOOK_PATH')
    return {'bot_token': bot_token, 'webhook_url': webhook_url, 'webhook_path': webhook_path}


def initial_bot(token: str) -> Bot:
    bot = Bot(token=token)
    return bot


async def handler(event, context) -> dict:
    logging.getLogger().setLevel(logging.INFO)
    envs = init_environment()
    bot = initial_bot(envs['bot_token'])
    logging.info("Bot has been started")
    path=f"{envs['webhook_url']}{envs['webhook_path']}"
    await bot.set_webhook(path )
    logging.info("Webhook has been set up")
    return {
        "statusCode": 200,
        "body": f"Webhook {path} has been set"
    }
