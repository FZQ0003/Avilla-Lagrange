from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from avilla.core import BaseAccount
from avilla.core.account import AccountStatus
from lagrange import Client

if TYPE_CHECKING:
    from .client import LagrangeClientService
    from .protocol import LagrangeProtocol


@dataclass
class LagrangeAccount(BaseAccount):
    status: AccountStatus = field(default_factory=AccountStatus)

    # Note: Do NOT use these properties for performance. Use ClientService instead.
    @property
    def protocol(self) -> 'LagrangeProtocol':
        return self.info.protocol  # noqa  # pyright: ignore [reportReturnType]

    @property
    def service(self) -> 'LagrangeClientService':
        return self.protocol.service.get_service(int(self.route['account']))

    @property
    def client(self) -> Client:
        return self.service.client

    @property
    def available(self) -> bool:
        return self.client.online.is_set()
