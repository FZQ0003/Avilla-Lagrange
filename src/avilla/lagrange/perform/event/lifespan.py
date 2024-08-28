from __future__ import annotations

from avilla.standard.core.account.event import (
    AccountRegistered,
    AccountUnregistered,
    AccountUnavailable,
)
from lagrange.client.client import Client
from lagrange.client.events.service import ClientOnline, ClientOffline, ServerKick
from loguru import logger

from ...account import LagrangeAccount
from ...capability import LagrangeCapability
from ...collector.connection import ConnectionCollector


class LagrangeEventLifespanPerform((m := ConnectionCollector())._):
    m.namespace = 'avilla.protocol/lagrange::event'
    m.identify = 'lifespan'

    @m.entity(LagrangeCapability.event_callback, raw_event=ClientOnline)
    async def online(self, raw_event: ClientOnline):
        account: LagrangeAccount = self.connection.account
        client: Client = self.connection.client
        account.status.enabled = True
        logger.info(f'Account {client.uin} online')
        return AccountRegistered(avilla=self.protocol.avilla, account=account)

    @m.entity(LagrangeCapability.event_callback, raw_event=ClientOffline)
    async def offline(self, raw_event: ClientOffline):
        account: LagrangeAccount = self.connection.account
        client: Client = self.connection.client
        account.status.enabled = False
        # Delete from avilla
        # if account.route in self.protocol.avilla.accounts:
        #     del self.protocol.avilla.accounts[account.route]
        logger.info(f"Account {client.uin} offline, it is {'' if raw_event.recoverable else 'not '}recoverable")
        return AccountUnregistered(avilla=self.protocol.avilla, account=account)

    @m.entity(LagrangeCapability.event_callback, raw_event=ServerKick)
    async def kicked(self, raw_event: ServerKick):
        account: LagrangeAccount = self.connection.account
        client: Client = self.connection.client
        account.status.enabled = False
        # Delete from avilla
        # if account.route in self.protocol.avilla.accounts:
        #     del self.protocol.avilla.accounts[account.route]
        logger.warning(f'Account {client.uin} was kicked: [{raw_event.title}] {raw_event.tips}')
        return AccountUnavailable(avilla=self.protocol.avilla, account=account)
