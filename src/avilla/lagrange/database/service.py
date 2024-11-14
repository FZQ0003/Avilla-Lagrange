from graia.amnesia.builtins.sqla import SqlalchemyService
from launart import Launart
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import selectinload

from .table import UserInfo, MessageRecord
from .types import Base


class LagrangeDatabaseService(SqlalchemyService):
    id = 'lagrange/database'

    async def launch(self, manager: Launart):
        async with self.stage('preparing'):
            logger.info('Initializing database...')
            await self.db.initialize()
            self.get_session = self.db.session_factory
            logger.success('Database initialized!')
        async with self.stage('blocking'):
            async with self.db.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.success('Database tables created!')
            await manager.status.wait_for_sigexit()
        async with self.stage('cleanup'):
            # async with self.get_session() as session:
            #     await session.commit()
            await self.db.stop()

    async def get_user(self, uin_or_uid: int | str) -> UserInfo:
        result = await self.select_first(select(UserInfo).where(
            UserInfo.uin == uin_or_uid if isinstance(uin_or_uid, int) else UserInfo.uid == uin_or_uid
        ))  # TODO: options
        if not result:
            raise ValueError(f'User not found: {uin_or_uid}')
        return result

    async def insert_user(self, uin: int, uid: str) -> None:
        try:
            await self.update_or_add(UserInfo(uin=uin, uid=uid))
        except InvalidRequestError as e:
            if 'persistent' not in str(e):
                raise e

    async def get_msg_record(self, msg_id: int = 0, seq: int = 0,
                             friend_uin: int = 0, group_uin: int = 0, target_uin: int = 0) -> MessageRecord:
        result = await self.select_first(select(MessageRecord).where(
            (MessageRecord.msg_id == msg_id) | (
                    (MessageRecord.seq == seq) &
                    (MessageRecord.friend_uin == friend_uin) &
                    (MessageRecord.target_uin.in_([target_uin, 0]))
            ) | (
                    (MessageRecord.seq == seq) &
                    (MessageRecord.group_uin == group_uin)
            )
        ).options(
            selectinload(MessageRecord.friend),
            selectinload(MessageRecord.group),
            selectinload(MessageRecord.target)
        ))
        if not result:
            raise ValueError(
                f'Message not found: msg_id = {msg_id}, seq = {seq}, '
                f'friend_uin = {friend_uin}, group_uin = {group_uin}, target_uin = {target_uin}'
            )
        return result

    async def insert_msg_record(self, record: MessageRecord) -> None:
        try:
            await self.update_or_add(record)
        except InvalidRequestError as e:
            if 'persistent' not in str(e):
                raise e
