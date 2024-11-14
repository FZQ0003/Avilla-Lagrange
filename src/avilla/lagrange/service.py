from typing import TYPE_CHECKING

from lagrange import Client
from launart import Service, Launart, any_completed
from launart.status import Phase

from .database import LagrangeDatabaseService

if TYPE_CHECKING:
    from .client import LagrangeClientService
    from .protocol import LagrangeProtocol, LagrangeGlobalConfig


class LagrangeService(Service):
    id = 'lagrange.service'
    protocol: 'LagrangeProtocol'
    service_map: dict[int, 'LagrangeClientService']
    database: LagrangeDatabaseService

    def __init__(self, protocol: 'LagrangeProtocol', config: 'LagrangeGlobalConfig'):
        super().__init__()
        self.protocol = protocol
        self.service_map = {}
        self.database = LagrangeDatabaseService(config.database_url, {'pool_pre_ping': True})

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
            manager.add_component(self.database)

        async with self.stage('blocking'):
            await any_completed(
                manager.status.wait_for_sigexit(),
                *(i.status.wait_for('blocking-completed') for i in self.service_map.values()),
                self.database.status.wait_for('blocking-completed')
            )

        async with self.stage('cleanup'):
            ...
