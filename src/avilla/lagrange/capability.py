from __future__ import annotations

from avilla.core.event import AvillaEvent
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.standard.core.application import AvillaLifecycleEvent
from graia.amnesia.message import Element, MessageChain
from graia.ryanvk import Fn, TypeOverload

from .types import Element as LgrElement
from .types import Event as LgrEvent


class LagrangeCapability((m := ApplicationCollector())._):
    @Fn.complex({TypeOverload(): ['raw_event']})
    async def event_callback(self, raw_event: ...) -> AvillaEvent | AvillaLifecycleEvent | None:
        ...

    @Fn.complex({TypeOverload(): ['raw_element']})
    async def deserialize_element(self, raw_element: ...) -> Element | None:  # type: ignore
        ...

    @Fn.complex({TypeOverload(): ['element']})
    async def serialize_element(self, element: ...) -> LgrElement | None:  # type: ignore
        ...

    async def deserialize_chain(self, chain: list[LgrElement]) -> MessageChain:
        # return MessageChain([await self.deserialize_element(_) for _ in chain])
        elements = []
        for lgr_element in chain:
            if element := await self.deserialize_element(lgr_element):
                elements.append(element)
        return MessageChain(elements)

    async def serialize_chain(self, chain: MessageChain) -> list[LgrElement]:
        # return [await self.serialize_element(_) for _ in chain]
        lgr_elements = []
        for element in chain:
            if lgr_element := await self.serialize_element(element):
                lgr_elements.append(lgr_element)
        return lgr_elements

    async def handle_event(self, event: LgrEvent):
        maybe_event = await self.event_callback(event)

        if maybe_event is not None:
            if (cx := getattr(maybe_event, 'context', None)) and cx.client.last_value == cx.self.last_value:
                return  # Do not record again (I don't know why)
            self.avilla.event_record(maybe_event)
            self.avilla.broadcast.postEvent(maybe_event)  # TODO: dispatcher to directly handle client & event
