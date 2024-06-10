from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import ydb  # type: ignore
from ydb import BaseSession, KeyBound, KeyRange
from ydb.aio import Driver

from tgbot.config import load_config

config = load_config()

FillDataQuery = """
        DECLARE $seriesData AS List<Struct<
            post_message_id: Uint32,
            manage_chat_id: Int32,
            manage_message_id: Uint32,
            channel_id: Int32,
            publication_at: Datetime 
             >>;
            
            REPLACE INTO delayed_post
            SELECT
                post_message_id,
                manage_message_id,
                manage_chat_id,
                channel_id,
                publication_at
            FROM AS_TABLE($seriesData);
    """


@dataclass
class PostInfo:
    post_message_id: int  # ID поста, который будет скопирован в Канал
    manage_message_id: int  # ID управляющего сообщения, где все кнопки
    manage_chat_id: int  # ID чата с ботом, где всё настраивается
    channel_id: int  # ID канала
    publication_at: datetime  # время публикации
    delete_at: datetime  # время удаления
    status: str  # статус сообщения


class PostInfoData(object):
    __slots__ = (
    "post_message_id", "manage_message_id", "manage_chat_id", "channel_id", "publication_at", "delete_at", "status")

    def __init__(self, post_message_id, manage_message_id, manage_chat_id, channel_id, publication_at, delete_at,
                 status):
        self.post_message_id = post_message_id
        self.manage_message_id = manage_message_id
        self.manage_chat_id = manage_chat_id
        self.channel_id = channel_id
        self.publication_at = publication_at
        self.delete_at = delete_at
        self.status = status


def get_series_data():
    return [
        PostInfoData(
            5,
            5,
            5,
            5
        ), PostInfoData(
            7,
            7,
            7,
            7
        ),
    ]


class PostsStoreHandler:
    _session: Optional[BaseSession] = None
    _driver: Optional[Driver] = None
    _table_name: str = 'delayed_post'
    _db_path: str

    def __init__(self, table_name: Optional[str] = None):
        if table_name:
            self._table_name = table_name
        self._db_path = config.yadb.db_config.database + "/" + self._table_name

    async def get_session(self) -> BaseSession:
        """ Получение сессии """
        if self._session is None:
            self._session = await self.create_session()
        return self._session

    async def create_session(self) -> BaseSession:
        """ Создание сесии """
        self._driver = ydb.aio.Driver(driver_config=config.yadb.db_config)
        await self._driver.wait(fail_fast=True)
        return await self._driver.table_client.session().create()

    async def stop_driver(self) -> None:
        """ Остановка драйвера """
        await self._driver.stop()

    async def get_data(self):
        session = await self.get_session()
        key_prefix_type = ydb.TupleType().add_element(
            ydb.PrimitiveType.Uint32)
        key_range = KeyRange(
            KeyBound((5,), key_prefix_type),
            KeyBound((5,), key_prefix_type)
        )
        async_response_iterator = await session.read_table(self._db_path,
                                                           columns=('post_message_id', 'manage_message_id'))
        async for item in async_response_iterator:
            # Process each item in the AsyncResponseIterator
            print(item)

    async def read_table(self, session, query):
        """
        Helper function to acquire session, execute `create_table` and release it
        """
        result = await session.execute_scheme(query)
        print("result query: ", result)

    # async def exec(self, post_data: PostInfo):

    # await pool.release(session)

    async def set_data(self):
        session = await self.get_session()
        prepared_query = await session.prepare(FillDataQuery)
        await session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query,
            {
                "$seriesData": get_series_data(),
            },
            commit_tx=True,
        )

    async def create_table(self):
        """ Создаём таблицу для отложенных постов """
        description = (
            ydb.TableDescription()
            .with_primary_keys("post_message_id", "manage_chat_id")
            .with_columns(
                ydb.Column("post_message_id", ydb.PrimitiveType.Uint32),
                ydb.Column("manage_message_id", ydb.PrimitiveType.Uint32),
                ydb.Column("manage_chat_id", ydb.PrimitiveType.Int32),
                ydb.Column("channel_id", ydb.PrimitiveType.Int32),
                ydb.Column('publication_at', ydb.PrimitiveType.Datetime),
                ydb.Column('delete_at', ydb.OptionalType(ydb.PrimitiveType.Datetime)),
                ydb.Column("status", ydb.PrimitiveType.Utf8)
            )
        )
        session = await self.get_session()
        await session.create_table(self._db_path, description)

    async def delete_table(self):
        """ Удаляем таблицу для отложенных постов """
        session = await self.get_session()
        await session.drop_table(self._db_path)
