from datetime import datetime

from avilla.core.context import Context
from avilla.core.elements import Reference
from avilla.core.message import Message
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageReceived, MessageRevoked
from lagrange.client.events.friend import FriendMessage
from lagrange.client.events.group import GroupMessage, GroupRecall
from loguru import logger

from ...account import LagrangeAccount
from ...capability import LagrangeCapability
from ...collector import LagrangeClientCollector
from ...utils.record import MessageRecord


class LagrangeEventMessagePerform((m := LagrangeClientCollector())._):
    m.namespace = 'avilla.protocol/lagrange::event'
    m.identify = 'message'

    async def message_handle(self, context, chain):
        account: LagrangeAccount = self.service.account
        message = await LagrangeCapability(
            account.staff.ext({'context': context})
        ).deserialize_chain(chain)
        reply = None
        if i := message.get(Reference):
            reply = i[0].message
            message = message.exclude(Reference)
        return message, reply

    @m.entity(LagrangeCapability.event_callback, raw_event=GroupMessage)
    async def group(self, raw_event: GroupMessage):
        self.database.insert_user(raw_event.uin, raw_event.uid)
        self.database.insert_msg_record(MessageRecord(
            friend_uin=raw_event.uin,
            seq=raw_event.seq,
            chain=raw_event.msg_chain,
            group_uin=raw_event.grp_id,
            time=raw_event.time
        ))
        if raw_event.uin == self.client.uin and not self.service.config.allow_self_msg:
            logger.info(f'Ignore: {raw_event}')
            return
        account: LagrangeAccount = self.service.account
        group: Selector = Selector().land(account.route['land']).group(str(raw_event.grp_id))
        member: Selector = group.member(str(raw_event.uin))
        context = Context(account, member, group, group, group.member(account.route['account']))
        message, reply = await self.message_handle(context, raw_event.msg_chain)
        return MessageReceived(
            context,
            Message(
                id=str(raw_event.seq),  # message_seq
                scene=group,
                sender=member,
                content=message,
                time=datetime.fromtimestamp(raw_event.time),
                reply=reply,
            ),
        )

    @m.entity(LagrangeCapability.event_callback, raw_event=FriendMessage)
    async def friend(self, raw_event: FriendMessage):
        self.database.insert_user(raw_event.from_uin, raw_event.from_uid)
        self.database.insert_user(raw_event.to_uin, raw_event.to_uid)
        self.database.insert_msg_record(MessageRecord(
            friend_uin=raw_event.from_uin,
            seq=raw_event.seq,
            chain=raw_event.msg_chain,
            target_uin=raw_event.to_uin,
            msg_id=raw_event.msg_id,
            time=raw_event.timestamp
        ))
        if raw_event.from_uin == self.client.uin and not self.service.config.allow_self_msg:
            logger.info(f'Ignore: {raw_event}')
            return
        account: LagrangeAccount = self.service.account
        land: Selector = Selector().land(account.route['land'])
        client: Selector = land.friend(str(raw_event.from_uin))
        endpoint: Selector = land.friend(str(raw_event.to_uin))
        # message from client, client == scene
        context = Context(account, client, endpoint, client, account.route)
        message, reply = await self.message_handle(context, raw_event.msg_chain)
        return MessageReceived(
            context,
            Message(
                id=str(raw_event.msg_id),
                scene=client,
                sender=client,
                content=message,
                time=datetime.fromtimestamp(raw_event.timestamp),
                reply=reply,
            ),
        )

    # TODO: MessageSent == GroupMessage / FriendMessage, but sender == self

    @m.entity(LagrangeCapability.event_callback, raw_event=GroupRecall)
    async def group_recall(self, raw_event: GroupRecall):
        account: LagrangeAccount = self.service.account
        group: Selector = Selector().land(account.route['land']).group(str(raw_event.grp_id))
        sender = group.member(str(self.database.get_user(raw_event.uid)[0]))
        message = group.message(str(raw_event.seq))
        operator = sender  # operator is unknown, use sender instead
        context = Context(account, operator, message, group, group.member(account.route['account']))
        return MessageRevoked(context=context, message=message, operator=operator, sender=sender)

    # TODO: FriendRecall (not implemented) and other possible message events
