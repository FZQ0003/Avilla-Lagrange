def import_performs():
    from . import context
    from .action import message
    from .compat import compat_apply_performs
    from .event import lifespan, message
    from .message import deserialize, serialize
    compat_apply_performs()
