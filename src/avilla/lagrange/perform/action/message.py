from datetime import datetime

from avilla.core import Context, CoreCapability
from avilla.core.elements import Reference
from avilla.core.message import Message
from avilla.core.selector import Selector
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

    @compat_collect(MessageSend.send, target='land.group')  # noqa
    async def send_group_msg(self, target: Selector, message: MessageChain,
                             *, reply: Selector | None = None) -> Selector:
        if message.has(Forward):
            raise NotImplementedError
            # return await self.send_group_forward_msg(target, message.get_first(Forward))
        if reply:
            message.content.insert(0, Reference(reply))
        client: Client = self.account.client
        seq = await client.send_grp_msg(
            await LagrangeCapability.from_self(self).serialize_chain(message),  # type: ignore
            int(target['group'])
        )
        context = self.account.get_context(target.member(self.account.route['account']))
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    str(seq),  # no msg_id
                    target,
                    context.client,
                    message,
                    datetime.now(),
                ),
                self.account,
            )
        )
        return Selector().land(self.account.route['land']).group(target.pattern['group']).message(str(seq))

    @compat_collect(MessageRevoke.revoke, target='land.group.message')  # noqa
    async def recall_group_msg(self, target: Selector):
        client: Client = self.account.client
        await client.recall_grp_msg(int(target['group']), int(target['message']))

    # @compat_collect(MessageRevoke.revoke, target='land.friend.message')
    # async def recall_friend_msg(self, target: Selector):
    #     client: Client = self.account.client
    #     raise NotImplementedError

    @compat_collect(MessageSend.send, target='land.friend')  # noqa
    async def send_friend_msg(self, target: Selector, message: MessageChain,
                              *, reply: Selector | None = None) -> Selector:
        if message.has(Forward):
            raise NotImplementedError
            # return await self.send_friend_forward_msg(target, message.get_first(Forward))
        if reply:
            message.content.insert(0, Reference(reply))
        client: Client = self.account.client
        chain = await LagrangeCapability.from_self(self).serialize_chain(message)
        seq = await client.send_friend_msg(
            chain,  # type: ignore
            self.protocol.service.database.get_user(int(target['friend']))[1]
        )
        # Manually insert into Database (lagrange-python will not record this)
        record = MessageRecord(
            friend_uin=client.uin,
            seq=seq,
            chain=chain,
            target_uin=int(target['friend']),
            msg_id=0  # TODO: msg_id
        )
        self.protocol.service.database.insert_msg_record(record)
        context = Context(
            self.account,
            self.account.route,
            target,
            target,
            self.account.route,
        )
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    str(record.msg_id),  # TODO: msg_id
                    target,
                    context.client,
                    message,
                    datetime.fromtimestamp(record.time),
                ),
                self.account,
            )
        )
        return Selector().land(self.account.route['land']).friend(target['friend']).message(str(seq))

    # TODO: send forward message (not implemented)

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
