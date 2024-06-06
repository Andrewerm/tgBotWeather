import asyncio
from dataclasses import dataclass

import ydb  # type: ignore

from tgbot.config import load_config

config = load_config()

queries = [  # Tables description to create
    """
    CREATE table `series` (
        `series_id` Uint64,
        `title` Utf8,
        `series_info` Utf8,
        `release_date` Date,
        PRIMARY KEY (`series_id`)
    )
    """
]

@dataclass
class PostInfo:
    post_message_id: int  # ID поста, который будет скопирован в Канал
    manage_message_id: int  # ID управляющего сообщения, где все кнопки
    manage_chat_id: int  # ID чата с ботом, где всё настраивается
    channel_id: int  # ID канала


class PostsStoreHandler:
    def get_data(self):
        pass

    async def create_table(self, session, query):
        """
        Helper function to acquire session, execute `create_table` and release it
        """
        await session.execute_scheme(query)
        print("created table, query: ", query)

    async def exec(self):
        async with ydb.aio.Driver(driver_config=config.yadb.db_config) as driver:
            await driver.wait(fail_fast=True)

            async with ydb.aio.SessionPool(driver, size=10) as pool:
                coros = [  # Generating coroutines to create tables concurrently
                    pool.retry_operation(self.create_table, query) for query in queries
                ]

                await asyncio.gather(*coros)  # Run table creating concurrently

                directory = await driver.scheme_client.list_directory(
                    ''
                )  # Listing database to ensure that tables are created
                print("Items in database:")
                for child in directory.children:
                    print(child.type, child.name)

    async def set_data(self):
        await self.exec()
