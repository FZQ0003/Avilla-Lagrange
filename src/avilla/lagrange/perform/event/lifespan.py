from avilla.standard.core.account.event import (
    AccountRegistered,
    AccountUnregistered,
    AccountUnavailable,
)
from lagrange.client.events.service import ClientOnline, ClientOffline, ServerKick
from loguru import logger

from ..base import LagrangePerform
from ...capability import LagrangeCapability


class LagrangeEventLifespanPerform(LagrangePerform):

    @LagrangeCapability.event_callback.collect(raw_event=ClientOnline)
    async def online(self, raw_event: ClientOnline) -> AccountRegistered:
        self.account.status.enabled = True
        logger.info(f'Account {self.client.uin} online')
        return AccountRegistered(avilla=self.avilla, account=self.account)

    @LagrangeCapability.event_callback.collect(raw_event=ClientOffline)
    async def offline(self, raw_event: ClientOffline) -> AccountUnregistered:
        self.account.status.enabled = False
        # Delete from avilla
        # if self.account.route in self.avilla.accounts:
        #     del self.avilla.accounts[self.account.route]
        logger.info(f'Account {self.client.uin} offline, it is'
                    f"{'' if raw_event.recoverable else ' not'} recoverable")
        return AccountUnregistered(avilla=self.avilla, account=self.account)

    @LagrangeCapability.event_callback.collect(raw_event=ServerKick)
    async def kicked(self, raw_event: ServerKick) -> AccountUnavailable:
        self.account.status.enabled = False
        # Delete from avilla
        # if self.account.route in self.avilla.accounts:
        #     del self.avilla.accounts[self.account.route]
        logger.warning(f'Account {self.client.uin} was kicked: [{raw_event.title}] {raw_event.tips}')
        return AccountUnavailable(avilla=self.avilla, account=self.account)
