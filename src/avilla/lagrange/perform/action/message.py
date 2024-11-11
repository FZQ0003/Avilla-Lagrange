from datetime import datetime

from avilla.core import Context, Message, Selector
from avilla.core.elements import Reference
from avilla.standard.core.message import MessageRevoke, MessageSend, MessageSent
from avilla.standard.qq.elements import Forward
from graia.amnesia.message import MessageChain

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
        # No need to post event
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
        # Manually insert into database & post event (lagrange-python will not record this)
        record = MessageRecord(
            friend_uin=self.client.uin,
            seq=seq,
            msg_chain=raw,  # type: ignore
            target_uin=int(target['friend']),
            msg_id=0  # TODO: msg_id
        )
        self.database.insert_msg_record(record)
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    id=str(record.seq),
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
        # No need to post event

    @compat_collect(MessageRevoke.revoke, target='land.friend.message')  # noqa
    async def recall_friend_msg(self, target: Selector):
        raise NotImplementedError('Not supported by lagrange-python')

    # TODO: send forward message (not implemented)
    def send_group_forward_msg(self, target: Selector, forward: Forward):
        raise NotImplementedError
