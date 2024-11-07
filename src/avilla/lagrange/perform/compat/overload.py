from avilla.core import Selector
from avilla.core.ryanvk.overload.target import TargetOverload
from flywheel import (
    FnOverload as FlywheelFnOverload,
    SimpleOverload as FlywheelSimpleOverload,
    TypeOverload as FlywheelTypeOverload
)
from flywheel_extras import (
    FnCollector,
    MappingOverload as FlywheelMappingOverload,
    PredicateOverload as FlywheelPredicateOverload,
)
from graia.ryanvk.overload import FnOverload, TypeOverload, NoneOverload, PredicateOverload


class FlywheelTargetOverload(FlywheelPredicateOverload):
    @staticmethod
    def predicate(collect_value: str, call_value: Selector) -> bool:  # type: ignore
        try:
            return call_value.follows(collect_value)
        except ValueError:
            return False


@FnCollector.set(FlywheelTypeOverload('overload'), as_default=True)
def convert_overload(overload: FnOverload, name: str) -> FlywheelFnOverload:
    return FlywheelSimpleOverload(name)


@convert_overload.collect(overload=TypeOverload)
def _impl_type(overload: TypeOverload, name: str) -> FlywheelTypeOverload:
    return FlywheelTypeOverload(name)


@convert_overload.collect(overload=NoneOverload)
def _impl_none(overload: NoneOverload, name: str) -> FlywheelFnOverload:
    return convert_overload(overload.bypassing, name)


@convert_overload.collect(overload=PredicateOverload)
def _impl_predicate(overload: PredicateOverload, name: str) -> FlywheelMappingOverload:
    return FlywheelMappingOverload(name, lambda _: overload.predicate('', _))


@convert_overload.collect(overload=TargetOverload)
def _impl_target(overload: TargetOverload, name: str) -> FlywheelTargetOverload:
    return FlywheelTargetOverload(name)
