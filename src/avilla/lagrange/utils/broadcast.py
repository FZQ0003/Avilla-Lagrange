from dataclasses import dataclass
from typing import Literal

from graia.broadcast import BaseDispatcher, Dispatchable, DispatcherInterface, ExecutionStop
from lagrange import Client
from lagrange.client.events import BaseEvent
from loguru import logger


@dataclass
class LagrangeRawEvent(Dispatchable):
    client: Client
    raw: BaseEvent

    class Dispatcher(BaseDispatcher):
        """A dispatcher to collect current Lagrange event."""

        @staticmethod
        async def catch(interface: DispatcherInterface['LagrangeRawEvent']):  # noqa # pyright: ignore
            if interface.annotation == LagrangeRawEvent:
                return interface.event
            if interface.name == 'raw_event' or interface.annotation == type(interface.event.raw):
                return interface.event.raw
            if issubclass(interface.annotation, BaseEvent):
                logger.warning(f'Raw event mismatch: {type(interface.event.raw)} -> {interface.annotation}')
                return interface.event.raw  # return normally
            if interface.annotation == Client:
                return interface.event.client


@dataclass
class AvillaLagrangeClientDispatcher(BaseDispatcher):
    """A dispatcher to collect current Lagrange client in avilla.

    Attributes:
        no_client_behavior: Behavior of the dispatcher if no client found.
    """
    no_client_behavior: Literal['stop', 'raise', 'continue'] = 'stop'

    # mixin = [LagrangeRawEvent.Dispatcher]

    def handle_error(self, default=None):
        if self.no_client_behavior == 'stop':
            raise ExecutionStop
        if self.no_client_behavior == 'raise':
            raise RuntimeError('No lagrange client found')
        logger.warning(f'No lagrange client found, return {default} instead')
        return default

    async def catch(self, interface: DispatcherInterface):
        from avilla.core import AvillaEvent
        from avilla.standard.core.account import AccountStatusChanged
        from .magic import get_avilla_from_broadcast
        from ..account import LagrangeAccount
        from ..protocol import LagrangeProtocol
        if interface.annotation == list[Client]:
            try:
                avilla = get_avilla_from_broadcast(interface.broadcast)
                protocol = avilla.get_protocol(LagrangeProtocol)
                return [_.client for _ in protocol.service.service_map.values()]
            except LookupError or ValueError:
                return self.handle_error([])
        if interface.annotation == Client:
            event = interface.event
            if isinstance(event, AccountStatusChanged):
                account = event.account
            elif isinstance(event, AvillaEvent):
                account = event.context.account
            else:
                account = None
            if isinstance(account, LagrangeAccount):
                return account.client
            return self.handle_error()
