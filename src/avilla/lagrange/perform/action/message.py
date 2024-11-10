from datetime import datetime

from avilla.core import Context, CoreCapability, Message, Selector
from avilla.core.elements import Reference
from avilla.standard.core.message import MessageRevoke, MessageSend
from avilla.standard.core.message.event import MessageSent
from avilla.standard.qq.elements import Forward
from graia.amnesia.message import MessageChain
from lagrange import Client

from ..base import LagrangePerform
from ..compat import compat_collect
from ...capability import LagrangeCapability
from ...utils.record import MessageRecord


class LagrangeMessageActionPerform(LagrangePerform):

    async def message_handle(self, context: Context, chain: MessageChain, reply: Selector | None = None):
        if reply:
            ref = Reference(reply)
        elif refs := chain.get(Reference, 1):
            ref = refs[0]
        else:
            ref = None
        chain = chain.exclude(Reference)  # Only one reference allowed
        if ref:
            chain.content.insert(0, ref)
        return await LagrangeCapability(
            self.protocol, self.account, context
        ).serialize_chain(chain), ref.message if ref else None

    @compat_collect(MessageSend.send, target='land.group')  # noqa
    async def send_group_msg(self, target: Selector, message: MessageChain,
                             *, reply: Selector | None = None) -> Selector:
        if forward := message.get(Forward, 1):
            return await self.send_group_forward_msg(target, forward[0])
        context = self.account.get_context(target.member(self.account.route['account']))
        raw, reply = await self.message_handle(context, message, reply)
        seq = await self.client.send_grp_msg(raw, int(target['group']))  # type: ignore
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    id=str(seq),  # no msg_id
                    scene=target,
                    sender=context.client,
                    content=message.exclude(Reference),
                    time=datetime.now(),
                    reply=reply
                ),
                self.account
            )
        )
        return target.message(str(seq))

    @compat_collect(MessageSend.send, target='land.friend')  # noqa
    async def send_friend_msg(self, target: Selector, message: MessageChain,
                              *, reply: Selector | None = None) -> Selector:
        if forward := message.get(Forward, 1):
            return await self.send_group_forward_msg(target, forward[0])
        context = self.account.get_context(target, via=self.account.route)
        raw, reply = await self.message_handle(context, message, reply)
        seq = await self.client.send_friend_msg(
            raw,  # type: ignore
            self.database.get_user(int(target['friend']))[1]
        )
        # Manually insert into Database (lagrange-python will not record this)
        record = MessageRecord(
            friend_uin=self.client.uin,
            seq=seq,
            chain=raw,  # type: ignore
            target_uin=int(target['friend']),
            msg_id=0  # TODO: msg_id
        )
        self.database.insert_msg_record(record)
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    id=str(record.msg_id),  # TODO: msg_id
                    scene=target,
                    sender=context.client,
                    content=message,
                    time=datetime.fromtimestamp(record.time),
                    reply=reply
                ),
                self.account
            )
        )
        return target.message(str(seq))

    @compat_collect(MessageRevoke.revoke, target='land.group.message')  # noqa
    async def recall_group_msg(self, target: Selector):
        await self.client.recall_grp_msg(int(target['group']), int(target['message']))
        context = self.account.get_context(target.member(self.account.route['account']))
        raise NotImplementedError('Recall successfully, but event not implemented')

    @compat_collect(MessageRevoke.revoke, target='land.friend.message')  # noqa
    async def recall_friend_msg(self, target: Selector):
        raise NotImplementedError('Not supported by lagrange-python')

    # TODO: send forward message (not implemented)
    def send_group_forward_msg(self, target: Selector, forward: Forward):
        raise NotImplementedError

    # TODO
    @compat_collect(CoreCapability.pull, target='land.group.message', route=Message)  # noqa
    async def get_group_message(self, message: Selector, route: ...) -> Message:
        client: Client = self.account.client
        messages = await client.get_grp_msg(
            int(message['group']),
            int(message['message']),
            filter_deleted_msg=False
        )
        if len(messages) < 1:
            raise RuntimeError(f"Failed to get message from {message['group']}: {message}")
        result = messages[-1]
        group = Selector().land(self.account.route['land']).group(message['group'])
        content = await LagrangeCapability.from_self(self).deserialize_chain(result.msg_chain)  # type: ignore
        return Message(
            str(result.seq),
            group,
            group.member(str(result.uin)),
            content,
            datetime.fromtimestamp(result.time),
        )

    # @compat_collect(CoreCapability.pull, target='land.friend.message', route=Message)  # noqa
    # async def get_friend_message(self, message: Selector, route: ...) -> Message:
    #     client: Client = self.account.client
    #     messages = await client.get_friend_msg(
    #         int(message['friend']),
    #         int(message['message']),
    #         filter_deleted_msg=False
    #     )
    #     if len(messages) < 1:
    #         raise RuntimeError(f"Failed to get message from {message['friend']}: {message}")
    #     result = messages[-1]
    #     friend = Selector().land(self.account.route['land']).friend(message['friend'])
    #     content = await LagrangeCapability.from_self(self).deserialize_chain(result.msg_chain)
    #     return Message(
    #         str(result.seq),
    #         friend,
    #         friend,
    #         content,
    #         datetime.fromtimestamp(result.timestamp),
    #     )
