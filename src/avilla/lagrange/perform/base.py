from typing import TYPE_CHECKING

from avilla.core import Avilla, Context
from flywheel_extras import FnCollection
from lagrange import Client
from typing_extensions import Self

if TYPE_CHECKING:
    from ..account import LagrangeAccount
    from ..client import LagrangeClientService
    from ..protocol import LagrangeProtocol
    from ..service import LagrangeDatabase


class LagrangePerform(FnCollection):
    avilla: Avilla
    protocol: 'LagrangeProtocol'
    database: 'LagrangeDatabase'
    service: 'LagrangeClientService'
    account: 'LagrangeAccount'
    client: Client
    context: Context | None = None

    def __init__(self, protocol: 'LagrangeProtocol', account: 'LagrangeAccount',
                 context: Context | None = None):
        self.avilla = protocol.avilla
        self.protocol = protocol
        self.database = protocol.service.database
        self.service = account.service
        self.account = account
        self.client = account.client
        if context:
            self.context = context

    @classmethod
    def from_self(cls, self: 'LagrangePerform') -> Self:
        return cls(self.protocol, self.account, self.context)
