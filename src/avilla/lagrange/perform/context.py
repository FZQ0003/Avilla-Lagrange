from avilla.core import CoreCapability, Selector, Context

from .base import LagrangePerform
from .compat import compat_collect


class LagrangeContextPerform(LagrangePerform):

    @compat_collect(CoreCapability.get_context, target='land.group')  # noqa
    def get_context_from_group(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target,
            target,
            target.member(self.account.route['account']),
        )

    @compat_collect(CoreCapability.get_context, target='land.friend')  # noqa
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

    @compat_collect(CoreCapability.get_context, target='land.stranger')  # noqa
    def get_context_from_stranger(self, target: Selector, *, via: Selector | None = None):
        return Context(self.account, target, self.account.route, target, self.account.route)

    @compat_collect(CoreCapability.get_context, target='land.group.member')  # noqa
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        return Context(
            self.account,
            target,
            target.into('::group'),
            target.into('::group'),
            target.into(f"~.member({self.account.route['account']})"),
        )

    @compat_collect(CoreCapability.channel, target='land.group')  # noqa
    @compat_collect(CoreCapability.channel, target='land.group.member')  # noqa
    @compat_collect(CoreCapability.guild, target='land.group')  # noqa
    @compat_collect(CoreCapability.guild, target='land.group.member')  # noqa
    def get_group(self, target: Selector):
        return target['group']

    @compat_collect(CoreCapability.user, target='land.group.member')  # noqa
    def get_member(self, target: Selector):
        return target['member']

    @compat_collect(CoreCapability.user, target='land.friend')  # noqa
    @compat_collect(CoreCapability.channel, target='land.friend')  # noqa
    def get_friend(self, target: Selector):
        return target['friend']

    @compat_collect(CoreCapability.user, target='land.stranger')  # noqa
    @compat_collect(CoreCapability.channel, target='land.stranger')  # noqa
    def get_stranger(self, target: Selector):
        return target['stranger']
