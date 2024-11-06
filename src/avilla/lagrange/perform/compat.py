from typing import ClassVar, TYPE_CHECKING

from avilla.core import Avilla, Context
from avilla.core.ryanvk.collector.base import AvillaBaseCollector
from graia.ryanvk import Access, OptionalAccess
from lagrange import Client

if TYPE_CHECKING:
    from ..client import LagrangeClientService
    from ..protocol import LagrangeProtocol
    from ..service import LagrangeDatabase


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

            context: OptionalAccess[Context] = OptionalAccess()

        return PerformTemplate


class LagrangeCompatPerform((m := LagrangeClientCollector())._):
    m.namespace = 'avilla.protocol/lagrange::compat'
    # from avilla.core.builtins.capability import CoreCapability
    # from avilla.standard.core.activity.capability import ActivityTrigger
    # from avilla.standard.core.message.capability import (
    #     MessageSend,
    #     MessageRevoke,
    #     MessageEdit,
    # )
    # from avilla.standard.core.privilege.capability import (
    #     PrivilegeCapability,
    #     MuteCapability,
    #     MuteAllCapability,
    #     BanCapability,
    # )
    # from avilla.standard.core.profile.capability import (
    #     SummaryCapability,
    #     NickCapability,
    #     AvatarFetch,
    # )
    # from avilla.standard.core.relation.capability import (
    #     SceneCapability,
    #     RequestJoinCapability,
    #     RelationshipTerminate,
    # )
    # from avilla.standard.core.request.capability import RequestCapability
    ...
