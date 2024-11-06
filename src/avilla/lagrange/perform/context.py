from typing import TYPE_CHECKING

from avilla.core import CoreCapability, Selector, Context
from avilla.core.ryanvk.collector.account import AccountCollector

if TYPE_CHECKING:
    from ..account import LagrangeAccount
    from ..protocol import LagrangeProtocol


class LagrangeContextPerform((m := AccountCollector['LagrangeProtocol', 'LagrangeAccount']())._):
    m.namespace = 'avilla.protocol/lagrange::context'

    @m.entity(CoreCapability.get_context, target='land.group')
    def get_context_from_group(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target,
            target,
            target.member(self.account.route['account']),
        )

    @m.entity(CoreCapability.get_context, target='land.friend')
    def get_context_from_friend(self, target: Selector, *, via: Selector | None = None):
        if via:
            return Context(
                self.account,
                via,
                target,
                target,
                self.account.route,
            )
        return Context(self.account, target, self.account.route, target, self.account.route)

    @m.entity(CoreCapability.get_context, target='land.stranger')
    def get_context_from_stranger(self, target: Selector, *, via: Selector | None = None):
        return Context(self.account, target, self.account.route, target, self.account.route)

    @m.entity(CoreCapability.get_context, target='land.group.member')
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into('::group'),
            target.into('::group'),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @m.entity(CoreCapability.channel, target='land.group')
    @m.entity(CoreCapability.channel, target='land.group.member')
    @m.entity(CoreCapability.guild, target='land.group')
    @m.entity(CoreCapability.guild, target='land.group.member')
    def get_group(self, target: Selector):
        return target['group']

    @m.entity(CoreCapability.user, target='land.group.member')
    def get_member(self, target: Selector):
        return target['member']

    @m.entity(CoreCapability.user, target='land.friend')
    @m.entity(CoreCapability.channel, target='land.friend')
    def get_friend(self, target: Selector):
        return target['friend']

    @m.entity(CoreCapability.user, target='land.stranger')
    @m.entity(CoreCapability.channel, target='land.stranger')
    def get_stranger(self, target: Selector):
        return target['stranger']
