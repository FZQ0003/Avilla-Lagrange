"""Some magic methods due to defects in Avilla & Avilla-* components."""
from contextlib import nullcontext

from avilla.core import Avilla, BaseProtocol, AvillaEvent
from avilla.core._runtime import cx_avilla, cx_context, cx_protocol  # noqa
from avilla.standard.core.application import AvillaLifecycleEvent
from graia.broadcast import Broadcast, Dispatchable


def get_avilla_from_broadcast(broadcast: Broadcast) -> Avilla:
    avilla: Avilla | None
    for f_dispatcher in broadcast.finale_dispatchers:
        if avilla := getattr(f_dispatcher, 'avilla', None):
            return avilla
    raise LookupError(f'Avilla not found in {broadcast}')


def avilla_post_event(avilla: Avilla,
                      event: Dispatchable,
                      upper_event: Dispatchable | None = None,
                      protocol: BaseProtocol | None = None):
    with (
        cx_avilla.use(avilla),
        cx_protocol.use(protocol) if protocol else nullcontext(),
        cx_context.use(event.context) if isinstance(event, AvillaEvent) else nullcontext()
    ):
        if isinstance(event, AvillaEvent | AvillaLifecycleEvent):
            avilla.event_record(event)
        return avilla.broadcast.postEvent(event, upper_event)
