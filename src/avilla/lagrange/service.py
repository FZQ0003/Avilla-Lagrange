from typing import TYPE_CHECKING

from launart import Service, Launart, any_completed
from launart.status import Phase

if TYPE_CHECKING:
    from .connection import LagrangeClientService
    from .protocol import LagrangeProtocol


class LagrangeService(Service):
    id = 'lagrange.service'

    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self) -> set[Phase]:
        return {'preparing', 'blocking', 'cleanup'}

    protocol: 'LagrangeProtocol'
    connection_map: dict[int, 'LagrangeClientService']

    def __init__(self, protocol: 'LagrangeProtocol'):
        super().__init__()
        self.protocol = protocol
        self.connection_map = {}

    def has_connection(self, uin: int):
        return uin in self.connection_map

    def get_connection(self, uin: int) -> 'LagrangeClientService':
        return self.connection_map[uin]

    async def launch(self, manager: Launart):
        async with self.stage('preparing'):
            for i in self.connection_map.values():
                manager.add_component(i)

        async with self.stage('blocking'):
            await any_completed(
                manager.status.wait_for_sigexit(),
                *(i.status.wait_for('blocking-completed') for i in self.connection_map.values())
            )

        async with self.stage('cleanup'):
            ...
