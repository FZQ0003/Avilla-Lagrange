from collections.abc import Callable
from functools import wraps
from typing import Concatenate, TypeVar, TYPE_CHECKING

from avilla.core.ryanvk.collector.account import AccountBasedPerformTemplate, AccountCollector
from flywheel.typing import P, R
from flywheel_extras.utils import get_method_class
from graia.ryanvk import Fn

from .base import LagrangePerform

if TYPE_CHECKING:
    from ..account import LagrangeAccount  # noqa: F401
    from ..protocol import LagrangeProtocol  # noqa: F401

T_Perform = TypeVar('T_Perform', bound=LagrangePerform)

m = AccountCollector['LagrangeProtocol', 'LagrangeAccount']()
m.namespace = 'avilla.protocol/lagrange::compat'

_TEMP_ENTITIES: dict[Callable, Callable] = {}
_TEMP_PERFORMS: dict[Callable, type[LagrangePerform]] = {}


def compat_collect(fn: Fn, **overload_settings):
    def wrapper(func: Callable[Concatenate[T_Perform, P], R]) -> Callable[Concatenate[T_Perform, P], R]:
        if not (entity := _TEMP_ENTITIES.get(func, None)):  # type: ignore
            @wraps(func)
            def entity(self: AccountBasedPerformTemplate, *args: P.args, **kwargs: P.kwargs) -> R:
                if not (perform := _TEMP_PERFORMS.get(func, None)):
                    _TEMP_PERFORMS[func] = perform = (
                        _ if (_ := get_method_class(func)) and issubclass(_, LagrangePerform)
                        else LagrangePerform
                    )
                return func(perform(self.protocol, self.account), *args, **kwargs)  # type: ignore

            _TEMP_ENTITIES[func] = entity
        fn.collect(m, **overload_settings)(entity)
        return func

    return wrapper


def compat_apply_performs():
    class _(m._): ...  # noqa
