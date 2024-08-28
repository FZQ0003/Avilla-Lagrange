from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from graia.amnesia.message import MessageChain

from avilla.core import Context
from avilla.core.elements import Reference
from avilla.core.message import Message
from avilla.core.ryanvk.collector.account import AccountCollector
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageRevoke, MessageSend
from avilla.standard.core.message.event import MessageSent
from avilla.standard.qq.elements import Forward
from lagrange import Client

from ...capability import LagrangeCapability

if TYPE_CHECKING:
    from ...account import LagrangeAccount  # noqa: F401
    from ...protocol import LagrangeProtocol  # noqa: F401


class LagrangeMessageActionPerform((m := AccountCollector['LagrangeProtocol', 'LagrangeAccount']())._):
    m.namespace = 'avilla.protocol/lagrange::action'
    m.identify = 'message'

    @MessageSend.send.collect(m, target='land.group')
    async def send_group_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        if message.has(Forward):
            raise NotImplementedError
            # return await self.send_group_forward_msg(target, message.get_first(Forward))
        if reply:
            message.content.insert(0, Reference(reply))
        client: Client = self.account.connection.client
        seq = await client.send_grp_msg(
            await LagrangeCapability(self.account.staff).serialize_chain(message),
            int(target['group'])
        )
        context = self.account.get_context(target.member(self.account.route['account']))
        self.protocol.post_event(
            MessageSent(
                context,
                Message(
                    str(seq),  # message_seq
                    target,
                    context.client,
                    message,
                    datetime.now(),
                ),
                self.account,
            )
        )
        return Selector().land(self.account.route['land']).group(target.pattern['group']).message(str(seq))

    @MessageRevoke.revoke.collect(m, target='land.group.message')
    async def recall_group_msg(self, target: Selector):
        client: Client = self.account.connection.client
        await client.recall_grp_msg(int(target['group']), int(target['message']))

    # @MessageRevoke.revoke.collect(m, target='land.friend.message')
    # async def recall_friend_msg(self, target: Selector):
    #     client: Client = self.account.connection.client
    #     raise NotImplementedError

    @MessageSend.send.collect(m, target='land.friend')
    async def send_friend_msg(
        self,
        target: Selector,
        message: MessageChain,
        *,
        reply: Selector | None = None,
    ) -> Selector:
        if message.has(Forward):
            raise NotImplementedError
            # return await self.send_friend_forward_msg(target, message.get_first(Forward))
        if reply:
            message.content.insert(0, Reference(reply))
        client: Client = self.account.connection.client
        seq = await client.send_friend_msg(
            await LagrangeCapability(self.account.staff).serialize_chain(message),
            self.account.get_uid(int(target['friend']))
        )
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
                    str(seq),  # message_seq
                    target,
                    context.client,
                    message,
                    datetime.now(),
                ),
                self.account,
            )
        )
        return Selector().land(self.account.route['land']).friend(target['friend']).message(str(seq))

    # TODO: send forward message (not implemented)

    @m.pull('land.group.message', Message)
    async def get_group_message(self, message: Selector, route: ...) -> Message:
        client: Client = self.account.connection.client
        messages = await client.get_grp_msg(
            int(message['group']),
            int(message['message']),
            filter_deleted_msg=False
        )
        if len(messages) < 1:
            raise RuntimeError(f"Failed to get message from {message['group']}: {message}")
        result = messages[-1]
        group = Selector().land(self.account.route['land']).group(message['group'])
        content = await LagrangeCapability(self.account.staff).deserialize_chain(result.msg_chain)
        return Message(
            str(result.seq),
            group,
            group.member(str(result.uin)),
            content,
            datetime.fromtimestamp(result.time),
        )

    # @m.pull('land.friend.message', Message)
    # async def get_friend_message(self, message: Selector, route: ...) -> Message:
    #     client: Client = self.account.connection.client
    #     messages = await client.get_friend_msg(
    #         int(message['friend']),
    #         int(message['message']),
    #         filter_deleted_msg=False
    #     )
    #     if len(messages) < 1:
    #         raise RuntimeError(f"Failed to get message from {message['friend']}: {message}")
    #     result = messages[-1]
    #     friend = Selector().land(self.account.route['land']).friend(message['friend'])
    #     content = await LagrangeCapability(self.account.staff).deserialize_chain(result.msg_chain)
    #     return Message(
    #         str(result.seq),
    #         friend,
    #         friend,
    #         content,
    #         datetime.fromtimestamp(result.timestamp),
    #     )
