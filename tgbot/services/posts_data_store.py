import logging
from enum import Enum
from typing import Optional

import ydb  # type: ignore
from ydb import BaseSession
from ydb.aio import Driver  # type: ignore

from tgbot.config import load_config

config = load_config()
logger = logging.getLogger(__name__)

FillDataQuery = """
        DECLARE $seriesData AS List<Struct<
            original_message_id: Uint32,
            copied_message_id: Optional<Uint32>,
            manage_chat_id: Int32,
            status: Utf8,
            manage_message_id: Uint32,
            channel_id: Int64,
            publication_at: Optional<Datetime>, 
            delete_at: Optional<Datetime>, 
             >>;
            
            REPLACE INTO delayed_post
            SELECT
                original_message_id,
                copied_message_id,
                manage_chat_id,
                status,
                manage_message_id,
                channel_id,
                publication_at,
                delete_at
            FROM AS_TABLE($seriesData);
    """

READ_DOCUMENT_TRANSACTION = """
DECLARE $original_message_id AS Uint32;
DECLARE $manage_chat_id AS Int32;
SELECT original_message_id,
                copied_message_id,
                manage_chat_id,
                status,
                manage_message_id,
                channel_id,
                publication_at,
                delete_at
FROM delayed_post
WHERE original_message_id = $original_message_id AND manage_chat_id = $manage_chat_id;
"""

READ_DELAYED_LIST_TRANSACTION = """
SELECT original_message_id,
                copied_message_id,
                manage_chat_id,
                status,
                manage_message_id,
                channel_id,
                publication_at,
                delete_at
FROM delayed_post
WHERE status="delayed" and publication_at<=CurrentUtcDatetime();
"""


class PostStatus(Enum):
    NEW = 'new'
    SENT = 'sent'
    DELAYED = 'delayed'


class PostInfoData(object):
    __slots__ = (
        "original_message_id", "copied_message_id", "manage_chat_id", "status", "manage_message_id", "channel_id",
        "publication_at", "delete_at")

    def __init__(self, original_message_id: int, manage_message_id: int, manage_chat_id: int,
                 channel_id: int,
                 status: PostStatus,
                 publication_at: Optional[int] = None,
                 copied_message_id: Optional[int] = None,
                 delete_at: Optional[int] = None):
        self.original_message_id = original_message_id  # ID поста, который будет скопирован в Канал
        self.copied_message_id = copied_message_id  # ID поста, который является копией в Канале
        self.manage_message_id = manage_message_id  # ID управляющего сообщения, где все кнопки
        self.manage_chat_id = manage_chat_id  # ID чата с ботом, где всё настраивается
        self.channel_id = channel_id  # ID канала
        self.publication_at = publication_at  # время публикации
        self.delete_at = delete_at  # время удаления
        self.status = status.value  # статус сообщения


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
        if self._driver:
            await self._driver.stop()

    async def get_data(self, original_message_id: int, manage_chat_id: int) -> Optional[dict]:
        session = await self.get_session()
        prepared = await session.prepare(READ_DOCUMENT_TRANSACTION)
        result_sets = await session.transaction().execute(prepared, {"$original_message_id": original_message_id,
                                                                     "$manage_chat_id": manage_chat_id},
                                                          commit_tx=True)
        if result_sets and result_sets[0] and result_sets[0].rows and result_sets[0].rows[0]:
            return result_sets[0].rows[0]
        else:
            return None

    async def set_data(self, data: PostInfoData) -> None:
        session = await self.get_session()
        prepared_query = await session.prepare(FillDataQuery)
        await session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query,
            {
                "$seriesData": [data],
            },
            commit_tx=True,
        )

    async def create_table(self):
        """ Создаём таблицу для отложенных постов """
        description = (
            ydb.TableDescription()
            .with_primary_keys("original_message_id", "manage_chat_id")
            .with_columns(
                ydb.Column("copied_message_id", ydb.OptionalType(ydb.PrimitiveType.Uint32)),
                ydb.Column("original_message_id", ydb.PrimitiveType.Uint32),
                ydb.Column("manage_message_id", ydb.PrimitiveType.Uint32),
                ydb.Column("manage_chat_id", ydb.PrimitiveType.Int32),
                ydb.Column("channel_id", ydb.PrimitiveType.Int64),
                ydb.Column('publication_at', ydb.OptionalType(ydb.PrimitiveType.Datetime)),
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

    async def update_status(self, original_message_id: int, manage_chat_id: int, new_status: PostStatus):
        """ Обновляет статус поста в БД """
        res = await self.get_data(original_message_id, manage_chat_id)
        if res:
            data = PostInfoData(original_message_id=res['original_message_id'],
                                copied_message_id=res['copied_message_id'],
                                manage_message_id=res['manage_message_id'],
                                manage_chat_id=res['manage_chat_id'],
                                channel_id=res['channel_id'],
                                publication_at=res['publication_at'],
                                delete_at=res['delete_at'], status=new_status)
            await self.set_data(data)
        else:
            logger.error(f'Пост с id <{original_message_id}> отсутствует в чате с ID <{manage_chat_id}>')

    async def exec_get_delayed_list(self) -> Optional[dict]:
        """ Выдаёт список постов, которые должны быть опубликованы к текущему времени """
        session = await self.get_session()
        prepared = await session.prepare(READ_DELAYED_LIST_TRANSACTION)
        result_sets = await session.transaction().execute(prepared, {},
                                                          commit_tx=True)
        if result_sets and result_sets[0]:
            return result_sets[0].rows
        else:
            return None
