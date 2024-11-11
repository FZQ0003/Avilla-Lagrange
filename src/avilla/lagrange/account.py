from dataclasses import dataclass, field
from functools import cached_property
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

    @cached_property
    def protocol(self) -> 'LagrangeProtocol':
        return self.info.protocol  # type: ignore

    @cached_property
    def service(self) -> 'LagrangeClientService':
        return self.protocol.service.get_service(int(self.route['account']))

    @cached_property
    def client(self) -> Client:
        return self.service.client

    @property
    def available(self) -> bool:
        return self.client.online.is_set()
