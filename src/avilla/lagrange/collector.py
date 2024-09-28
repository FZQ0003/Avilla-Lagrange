from typing import ClassVar, TYPE_CHECKING

from avilla.core import Avilla
from avilla.core.ryanvk.collector.base import AvillaBaseCollector
from graia.ryanvk import Access
from lagrange import Client

if TYPE_CHECKING:
    from .client import LagrangeClientService
    from .protocol import LagrangeProtocol
    from .service import LagrangeDatabase


class LagrangeClientCollector(AvillaBaseCollector):
    post_applying: bool = False

    @property
    def _(self):
        upper = super()._

        class PerformTemplate(upper, native=True):
            __collector__: ClassVar[LagrangeClientCollector]

            service: Access['LagrangeClientService'] = Access()
            protocol: Access['LagrangeProtocol'] = Access()
            client: Access[Client] = Access()
            database: Access['LagrangeDatabase'] = Access()
            avilla: Access[Avilla] = Access()

        return PerformTemplate
