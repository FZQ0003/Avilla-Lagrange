from datetime import datetime

from avilla.core import Context, Message
from avilla.core.elements import Reference
from avilla.standard.core.message import MessageReceived, MessageRevoked, MessageSent
from lagrange.client.events.friend import FriendMessage, FriendRecall
from lagrange.client.events.group import GroupMessage, GroupRecall
from loguru import logger

from ..base import LagrangePerform
from ...capability import LagrangeCapability
from ...const import LAND_SELECTOR
from ...typing import RawMessage
from ...utils.record import MessageRecord


class LagrangeEventMessagePerform(LagrangePerform):

    async def message_handle(self, context: Context, raw: RawMessage) -> Message:
        content = await LagrangeCapability(
            self.protocol, self.account, context
        ).deserialize_chain(raw.msg_chain)
        reply = None
        if refs := content.get(Reference, 1):
            reply = refs[0].message
            content = content.exclude(Reference)
        if time_int := (getattr(raw, 'timestamp', 0) or getattr(raw, 'time', 0)):
            timestamp = datetime.fromtimestamp(time_int)
        else:
            timestamp = datetime.now()
        return Message(
            id=str(raw.seq),  # message_seq
            scene=context.scene,
            sender=context.client,
            content=content,
            time=timestamp,
            reply=reply
        )

    @LagrangeCapability.event_callback.collect(raw_event=GroupMessage)
    async def group_message(self, raw_event: GroupMessage):
        self.database.insert_user(raw_event.uin, raw_event.uid)
        self.database.insert_msg_record(MessageRecord(
            friend_uin=raw_event.uin,
            seq=raw_event.seq,
            msg_chain=raw_event.msg_chain,  # type: ignore
            group_uin=raw_event.grp_id,
            msg_id=raw_event.rand,
            time=raw_event.time
        ))
        context = self.account.get_context(
            LAND_SELECTOR.group(str(raw_event.grp_id)).member(str(raw_event.uin))
        )
        message = await self.message_handle(context, raw_event)
        if raw_event.uin == self.client.uin:
            return MessageSent(context, message, self.account)
        return MessageReceived(context, message)

    @LagrangeCapability.event_callback.collect(raw_event=FriendMessage)
    async def friend_message(self, raw_event: FriendMessage):
        self.database.insert_user(raw_event.from_uin, raw_event.from_uid)
        self.database.insert_msg_record(MessageRecord(
            friend_uin=raw_event.from_uin,
            seq=raw_event.seq,
            msg_chain=raw_event.msg_chain,
            target_uin=raw_event.to_uin,
            msg_id=raw_event.msg_id,
            time=raw_event.timestamp
        ))
        if raw_event.to_uin == self.client.uin:
            context = self.account.get_context(LAND_SELECTOR.friend(str(raw_event.from_uin)))
        else:
            logger.warning(f'Message target is not self: {raw_event}')
            self.database.insert_user(raw_event.to_uin, raw_event.to_uid)
            context = self.account.get_context(
                LAND_SELECTOR.friend(str(raw_event.to_uin)),
                via=LAND_SELECTOR.friend(str(raw_event.from_uin))
            )
        message = await self.message_handle(context, raw_event)
        if raw_event.from_uin == self.client.uin:
            return MessageSent(context, message, self.account)
        return MessageReceived(context, message)

    @LagrangeCapability.event_callback.collect(raw_event=GroupRecall)
    async def group_recall(self, raw_event: GroupRecall):
        # Operator is unknown, use sender as client instead
        group = LAND_SELECTOR.group(str(raw_event.grp_id))
        context = self.account.get_context(
            group.message(str(raw_event.seq)),
            via=group.member(str(self.database.get_user(raw_event.uid)[0]))
        )
        return MessageRevoked(
            context=context,
            message=context.endpoint,
            operator=context.client,
            sender=context.client
        )

    @LagrangeCapability.event_callback.collect(raw_event=FriendRecall)
    async def friend_recall(self, raw_event: FriendRecall):
        # Operator is sender
        context = self.account.get_context(
            LAND_SELECTOR.friend(str(raw_event.to_uin)).message(str(raw_event.seq))
        )
        return MessageRevoked(
            context=context,
            message=context.endpoint,
            operator=context.client,
            sender=context.client
        )
