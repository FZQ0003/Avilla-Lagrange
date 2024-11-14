from typing import cast

from avilla.core import CoreCapability, Message, Selector, MessageReceived, MessageSent

from .base import LagrangePerform
from .compat import compat_collect
from .event.message import LagrangeEventMessagePerform
from ..capability import LagrangeCapability
from ..typing import RawMessage


class LagrangeMetadataPerform(LagrangePerform):

    @compat_collect(CoreCapability.pull, target='land.group.message', route=Message)  # noqa
    async def get_group_message(self, message: Selector, route: ...) -> Message:
        try:
            # Search from database
            record = await self.database.get_msg_record(
                seq=int(message['message']),
                group_uin=int(message['group'])
            )
            return await LagrangeEventMessagePerform.from_self(self).message_handle(
                self.account.get_context(message.into('::group').member(str(record.friend_uin))),
                cast(RawMessage, record)
            )
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
            event = cast(
                MessageReceived | MessageSent,
                await LagrangeCapability.from_self(self).event_callback(messages[-1])
            )
            return event.message

    @compat_collect(CoreCapability.pull, target='land.friend.message', route=Message)  # noqa
    @compat_collect(CoreCapability.pull, target='land.stranger.message', route=Message)  # noqa
    async def get_private_message(self, message: Selector, route: ...) -> Message:
        raise NotImplementedError('Not supported by lagrange-python')
