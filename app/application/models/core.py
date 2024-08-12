from typing import Any, Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ...logger.logger import logger_database
from .models import Attachments, Base

logger = logger_database


class DatabaseManger:
    ECHO = False
    EXPIRE_ON_COMMIT = False

    def __init__(self, database_url: str) -> None:
        self.url = database_url
        self.engine: AsyncEngine = create_async_engine(url=self.url, echo=self.ECHO)
        logger.debug("Initial engine %s", self.url)
        logger.debug("Engine echo %s", self.ECHO)

    async def initial_database(self) -> None:
        """Инициализирует базу данных, создаёт таблицы"""
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        logger.info("Initialization database")

    async def drop_all_table(self) -> None:
        """Удаляет все таблицы из базы данных"""
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        logger.info("Info delete all table")

    async def get_session(self) -> AsyncSession:
        """Вспомогательная функция для получения сессии в контекстном менеджере.
        Возвращает асинхронную сессию AsyncSession

        Returns:
            AsyncSession
        """
        _session = async_sessionmaker(
            bind=self.engine, expire_on_commit=self.EXPIRE_ON_COMMIT
        )
        session: AsyncSession = _session()
        return session

    async def close(self) -> None:
        """Закрытие всех соединений и транзакций"""
        await self.engine.dispose()
        logger.info("Close database")


class SQLManager(DatabaseManger):

    async def add(self, *args) -> None:
        """Функция добавляет объекты модели в базу данных
        Принимает в виде аргументов объекты модели.
        Пример > await add(user_1: Users, user_2: Tweets)
        """
        async with await self.get_session() as session:
            async with session.begin():
                session.add_all(args)
                await session.commit()

    async def delete(self, obj) -> None:
        """Удаляет объект из базы данных
        Args:
            obj Any: Объект модели базы данных
        """
        async with await self.get_session() as session:
            async with session.begin():
                await session.delete(obj)
                await session.commit()

    async def select_scalars_all(self, stmt: Select) -> Sequence:
        """Возвращает все объекты из базы данных по Select

        Args:
            stmt (Select): объект запроса

        Returns:
            Sequence: Список объектов
        """
        async with await self.get_session() as session:
            async with session.begin():
                result = await session.execute(stmt)
                object_list = result.scalars().all()
        return object_list

    async def select_scalars_one_or_none(self, stmt: Select) -> Any | None:
        """Возвращает объект по запросу Select или None
        Если такой объект не найден

        Args:
            stmt (Select): объект запроса

        Returns:
            Any | None: Объект модели баз данных
        """
        async with await self.get_session() as session:
            async with session.begin():
                result = await session.execute(stmt)
                object = result.scalars().one_or_none()
            return object

    async def attachments_update_tweet_id(
        self, attachments_ids: list[int], tweet_id: int
    ):
        """Вспомогательная функция для обновления Attachments
        Обновляет tweet_id ссылку на объект Tweets

        Args:
            attachments_ids (list[int]): Список id моделей Attachments
            tweet_id (int): id объекта Tweets
        """
        async with await self.get_session() as session:
            result = await session.execute(
                select(Attachments).filter(Attachments.id.in_(attachments_ids))
            )
            for attachment in result.scalars().all():
                attachment.tweet_id = tweet_id
            await session.commit()

    async def add_attachment(self, attachment: Attachments, file_name: str) -> None:
        """Вспомогательная функция. Добавляет в базу данных Attachments
        и обновляет имя файла и ссылку в объекте Attachments
        К имени файла добавляется id для уникальности.
        Таким образом для у каждой картинки будет уникальное имя файла,
        привязанное к объекту модели Attachments

        Args:
            attachment (Attachments): объект модели базы данных Attachments
            file_name (str): имя файла
        """
        async with await self.get_session() as session:
            async with session.begin():
                session.add(attachment)
                await session.commit()
            async with session.begin():
                attachment.file_name = "{id}_{filename}".format(
                    id=attachment.id, filename=file_name
                )
                attachment.link = "images/{filename}".format(
                    filename=attachment.file_name
                )
                await session.commit()
