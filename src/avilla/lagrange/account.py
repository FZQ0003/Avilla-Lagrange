from dataclasses import dataclass
from typing import TYPE_CHECKING

from avilla.core import BaseAccount, Selector
from avilla.core.account import AccountStatus

if TYPE_CHECKING:
    from .connection import LagrangeClientService
    from .protocol import LagrangeProtocol


@dataclass
class LagrangeAccount(BaseAccount):
    protocol: 'LagrangeProtocol'
    status: AccountStatus

    # oid_map[group][member]    => openid of group member
    # oid_map[0][friend]        => openid of friend
    # oid_map[group][0]         => openid of group

    # uin <=> uid
    # TODO: use a database?
    uid_map: dict[int, str]

    def __init__(self, route: Selector, protocol: 'LagrangeProtocol'):
        super().__init__(route, protocol.avilla)
        self.protocol = protocol
        self.status = AccountStatus()
        self.uid_map = {}

    # def oid_to_selector(self, oid: str) -> Selector | None:
    #     for group_uin, group_map in self.oid_map.items():
    #         for member_uin, member_oid in group_map.items():
    #             if member_oid == oid:
    #                 land = Selector().land(self.route['land'])
    #                 if group_uin:
    #                     selector = land.group(str(group_uin))
    #                     return selector.member(str(member_uin)) if member_uin else selector
    #                 else:
    #                     return land.friend(str(member_uin)) if member_uin else self.route

    def get_uid(self, uin: int) -> str:
        return self.uid_map.get(uin, '')

    def get_uin(self, uid: str) -> int:
        for _uin, _uid in self.uid_map.items():
            if _uid == uid:
                return _uin
        return 0

    @property
    def connection(self) -> 'LagrangeClientService':
        return self.protocol.service.get_connection(int(self.route['account']))

    @property
    def available(self) -> bool:
        return self.status.available
