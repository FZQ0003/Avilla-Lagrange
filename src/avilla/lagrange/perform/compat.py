import inspect
from collections.abc import Callable
from typing import Concatenate, TypeVar, TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountBasedPerformTemplate, AccountCollector
from flywheel.typing import P, R
# from flywheel_extras.utils import get_method_class  # TODO
from graia.ryanvk import Fn

from .base import LagrangePerform

if TYPE_CHECKING:
    from ..account import LagrangeAccount  # noqa: F401
    from ..protocol import LagrangeProtocol  # noqa: F401

T_Perform = TypeVar('T_Perform', bound=LagrangePerform)

m = AccountCollector['LagrangeProtocol', 'LagrangeAccount']()
m.namespace = 'avilla.protocol/lagrange::compat'


def _get_method_class(method: Callable) -> type | None:
    if not (module := inspect.getmodule(method)):
        return
    for _, cls in inspect.getmembers(module, lambda _: inspect.isclass(_) and inspect.getmodule(_) is module):
        if hasattr(cls, method.__name__):
            return cls


def compat_collect(fn: Fn, **overload_settings):
    def wrapper(func: Callable[Concatenate[T_Perform, P], R]) -> Callable[Concatenate[T_Perform, P], R]:
        def real_entity(self: AccountBasedPerformTemplate, *args: P.args, **kwargs: P.kwargs) -> R:
            cls = _ if (_ := _get_method_class(func)) and issubclass(_, LagrangePerform) else LagrangePerform
            return func(cls(self.protocol, self.account), *args, **kwargs)  # type: ignore

        fn.collect(m, **overload_settings)(real_entity)
        return func

    return wrapper


def compat_apply_performs():
    class _(m._): ...  # noqa
