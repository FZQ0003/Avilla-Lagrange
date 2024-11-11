from typing import TYPE_CHECKING

from lagrange import Client
from launart import Service, Launart, any_completed
from launart.status import Phase

from .utils.database import Database, Table
from .utils.record import MessageRecord

if TYPE_CHECKING:
    from .client import LagrangeClientService
    from .protocol import LagrangeProtocol, LagrangeGlobalConfig


class LagrangeDatabase(Database):

    def __init__(self, path: str = ':memory:'):
        super().__init__(path, (
            Table({'uin': int, 'uid': str}, 'user_id', 'uin'),
            Table(MessageRecord, 'message_record', 'msg_id')
        ))

    def get_user(self, uin_or_uid: int | str) -> tuple[int, str]:
        table = self._tables[0]
        if isinstance(uin_or_uid, int):
            result = table.execute(
                table.sql_select(['uin'], use_primary_key=False),
                {'uin': uin_or_uid}
            )
        else:
            result = table.execute(
                table.sql_select(['uid'], use_primary_key=False),
                {'uid': uin_or_uid}
            )
        if result:
            return result[0]['uin'], result[0]['uid']
        raise ValueError(f'User not found: {uin_or_uid}')

    def insert_user(self, uin: int, uid: str) -> None:
        table = self._tables[0]
        table.execute(table.sql_insert(), {'uin': uin, 'uid': uid})

    def get_msg_record(self, msg_id: int = 0, seq: int = 0,
                       friend_uin: int = 0, group_uin: int = 0, target_uin: int = 0) -> MessageRecord:
        table = self._tables[1]
        result = table.execute(
            'SELECT * FROM message_record '
            'WHERE msg_id = ? '
            'OR seq = ? AND friend_uin = ? AND target_uin IN (?, 0) '
            'OR seq = ? AND group_uin = ?',
            (msg_id, seq, friend_uin, target_uin, seq, group_uin)
        )
        if result:
            return result[0]
        raise ValueError(
            f'Message not found: msg_id = {msg_id}, seq = {seq}, '
            f'friend_uin = {friend_uin}, group_uin = {group_uin}, target_uin = {target_uin}'
        )

    def insert_msg_record(self, record: MessageRecord):
        table = self._tables[1]
        table.execute(table.sql_insert(), record)


class LagrangeService(Service):
    id = 'lagrange.service'
    protocol: 'LagrangeProtocol'
    service_map: dict[int, 'LagrangeClientService']
    database: LagrangeDatabase

    def __init__(self, protocol: 'LagrangeProtocol', config: 'LagrangeGlobalConfig'):
        super().__init__()
        self.protocol = protocol
        self.service_map = {}
        self.database = LagrangeDatabase(str(config.database_path))

    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self) -> set[Phase]:
        return {'preparing', 'blocking', 'cleanup'}

    def has_client(self, uin: int):
        return uin in self.service_map

    def get_client(self, uin: int) -> Client:
        return self.get_service(uin).client

    def get_service(self, uin: int) -> 'LagrangeClientService':
        return self.service_map[uin]

    async def launch(self, manager: Launart):
        async with self.stage('preparing'):
            for i in self.service_map.values():
                manager.add_component(i)
            self.database.connect()

        async with self.stage('blocking'):
            await any_completed(
                manager.status.wait_for_sigexit(),
                *(i.status.wait_for('blocking-completed') for i in self.service_map.values())
            )

        async with self.stage('cleanup'):
            self.database.close(save=True)
