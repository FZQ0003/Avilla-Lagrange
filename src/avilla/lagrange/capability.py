from avilla.core import AvillaEvent
from avilla.standard.core.application import AvillaLifecycleEvent
from flywheel import TypeOverload as TypeOverload
from flywheel_extras import FnCollector
from graia.amnesia.message import Element, MessageChain
from lagrange import Client
from loguru import logger

from .perform.base import LagrangePerform
from .types import Element as LgrElement
from .types import Event as LgrEvent
from .utils.broadcast import LagrangeRawEvent
from .utils.magic import avilla_post_event


class LagrangeCapability(LagrangePerform):
    @FnCollector.set(TypeOverload('raw_event'))
    async def event_callback(self, raw_event: LgrEvent) -> AvillaEvent | AvillaLifecycleEvent | None:
        ...

    @FnCollector.set(TypeOverload('raw_element'))
    async def deserialize_element(self, raw_element: LgrElement) -> Element | None:
        ...

    @FnCollector.set(TypeOverload('element'))
    async def serialize_element(self, element: Element) -> LgrElement | None:
        ...

    async def deserialize_chain(self, chain: list[LgrElement]) -> MessageChain:
        return MessageChain([__ for _ in chain if (__ := await self.deserialize_element(_))])

    async def serialize_chain(self, chain: MessageChain) -> list[LgrElement]:
        return [__ for _ in chain if (__ := await self.serialize_element(_))]

    async def handle_event(self, client: Client, event: LgrEvent):
        try:
            if maybe_event := await self.event_callback(event):
                # if (cx := getattr(maybe_event, 'context', None)) and cx.client.last_value == cx.self.last_value:
                #     return  # Do not record again
                avilla_post_event(self.avilla, maybe_event, LagrangeRawEvent(client, event), self.protocol)
        except NotImplementedError:
            logger.warning(f'Client {client.uin} received unsupported event: {type(event).__name__}')
