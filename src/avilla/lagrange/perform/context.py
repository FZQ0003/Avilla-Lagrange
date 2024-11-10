from avilla.core import CoreCapability, Selector, Context

from .base import LagrangePerform
from .compat import compat_collect


# TODO: Use strings like '::group.*'
#       I don't know how to search implementations with `TargetOverload`.
class LagrangeContextPerform(LagrangePerform):
    # In land, there are 4 types of selectors describing a person:
    # * `land.account` representing the bot itself
    # * `land.friend` in a private chat
    # * `land.group.member` in a group (`land.group`)
    # * `land.stranger` in a temporary chat
    # Use `land.account` as self for common chats, and `land.group.member` for groups.

    @compat_collect(CoreCapability.get_context, target='land.group')  # noqa
    def get_context_from_group(self, target: Selector, *, via: Selector | None = None):
        # self == land.group.member
        # via => Context(scene=target, client=via, endpoint=scene)
        # no via => notice => Context(scene=target, client=scene, endpoint=self)
        context_self = target.member(self.account.route['account'])
        return Context(
            self.account,
            via or target,
            target if via else context_self,
            target,
            context_self
        )

    @compat_collect(CoreCapability.get_context, target='land.group.member')  # noqa
    def get_context_from_member(self, target: Selector, *, via: Selector | None = None):
        # self == land.group.member
        # via => notice => Context(scene=land.group, client=via, endpoint=target)
        # no via => Context(scene=land.group, client=target, endpoint=scene)
        context_scene = target.into('::group')
        return Context(
            self.account,
            via or target,
            target if via else context_scene,
            context_scene,
            context_scene.member(self.account.route['account'])
        )

    @compat_collect(CoreCapability.get_context, target='land.friend')  # noqa
    @compat_collect(CoreCapability.get_context, target='land.friend', via='land.account')  # noqa
    @compat_collect(CoreCapability.get_context, target='land.stranger')  # noqa
    def get_context_from_private(self, target: Selector, *, via: Selector | None = None):
        # self == land.account
        # If via == land.account, then scene == target
        # via => Context(scene=<via or target>, client=via, endpoint=target)
        # no via => Context(scene=target, client=target, endpoint=self)
        return Context(
            self.account,
            via or target,
            target if via else self.account.route,
            target if via and via.follows('::account') else via or target,
            self.account.route
        )

    @compat_collect(CoreCapability.get_context, target='land.message')  # noqa
    def get_context_from_message(self, target: Selector, *, via: Selector | None = None):
        # target == land.<unknown>.message
        # via == operator of the message => Context(scene=land.?, client=via, endpoint=land.?.message)
        # no via => search database => Context(scene=land.?, client=scene, endpoint=land.?.message)
        # TODO: get_context_from_message
        raise NotImplementedError('The scene of this message is unknown')

    @compat_collect(CoreCapability.get_context, target='land.group.message')  # noqa
    @compat_collect(CoreCapability.get_context, target='land.friend.message')  # noqa
    @compat_collect(CoreCapability.get_context, target='land.stranger.message')  # noqa
    def get_context_from_scene_message(self, target: Selector, *, via: Selector | None = None):
        # Same as get_context_from_message, but scene can be extracted from target
        context_scene = Selector({_k: _v for _k, _v in target.items() if _k != 'message'})
        return Context(
            self.account,
            via or context_scene,
            target,
            context_scene,
            context_scene.member(self.account.route['account'])
            if context_scene.last_key == 'group' else self.account.route
        )

    @compat_collect(CoreCapability.get_context, target='land.group.member.message')  # noqa
    def get_context_from_group_member_message(self, target: Selector, *, via: Selector | None = None):
        # DO NOT USE THIS FUNCTION, TARGET HERE IS INVALID
        context_scene = target.into('::group')
        return Context(
            self.account,
            via or target.into('::group.member'),
            Selector({_k: _v for _k, _v in target.items() if _k != 'member'}),
            context_scene,
            context_scene.member(self.account.route['account'])
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

    @compat_collect(CoreCapability.user, target='land.account')  # noqa
    @compat_collect(CoreCapability.channel, target='land.account')  # noqa
    def get_account(self, target: Selector):
        return target['account']
