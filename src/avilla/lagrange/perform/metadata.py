from avilla.core import CoreCapability, Message, Selector

from .base import LagrangePerform
from .compat import compat_collect
from .event.message import LagrangeEventMessagePerform
from ..capability import LagrangeCapability


class LagrangeMetadataPerform(LagrangePerform):

    @compat_collect(CoreCapability.pull, target='land.group.message', route=Message)  # noqa
    async def get_group_message(self, message: Selector, route: ...) -> Message:
        try:
            # Search from database
            record = self.database.get_msg_record(seq=int(message['message']), group_uin=int(message['group']))
            context = self.account.get_context(message.into('::group').member(str(record.friend_uin)))
            return await LagrangeEventMessagePerform.from_self(self).message_handle(context, record)
        except ValueError:
            # Call lagrange-python
            messages = await self.client.get_grp_msg(
                int(message['group']),
                int(message['message']),
                filter_deleted_msg=False
            )
            if len(messages) < 1:
                raise RuntimeError(f"Failed to get message from {message['group']}: {message}")
            # GroupMessage -> MessageReceived | MessageSent
            event = await LagrangeCapability.from_self(self).event_callback(messages[-1])
            return event.message  # noqa

    @compat_collect(CoreCapability.pull, target='land.friend.message', route=Message)  # noqa
    @compat_collect(CoreCapability.pull, target='land.stranger.message', route=Message)  # noqa
    async def get_private_message(self, message: Selector, route: ...) -> Message:
        raise NotImplementedError('Not supported by lagrange-python')
