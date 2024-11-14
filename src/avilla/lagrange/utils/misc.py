import base64
import builtins
import json
from collections.abc import Generator

from dataclasses import fields, is_dataclass
from importlib import import_module
from types import ModuleType
from typing import Any, TypeVar

T = TypeVar('T')


def object_to_type_str(obj: Any) -> str:
    if isinstance(obj, ModuleType):
        return obj.__name__
    if not isinstance(obj, type):
        obj = type(obj)
    class_name = repr(obj).split("'")[1]
    module_name = obj.__module__
    if not class_name.startswith(module_name):
        class_name = module_name + '.' + class_name
    # format: module.class
    return class_name


def type_str_to_object(type_str: str) -> ModuleType | type | None:
    cls_list = type_str.split('.')
    try:
        cls = import_module(cls_list[0])
        cls_list.pop(0)
    except ModuleNotFoundError:
        cls = builtins
    for attr in cls_list:
        if not (cls := getattr(cls, attr, None)):
            break
    return cls


def get_fields(obj: Any) -> dict[str, type]:
    if is_dataclass(obj):
        output = {}
        for field in fields(obj):  # noqa
            if field.init:
                if isinstance(field.type, str):
                    o_type = type_str_to_object(field.type)
                    if isinstance(o_type, type):
                        output[field.name] = o_type
                else:
                    output[field.name] = field.type
        return output
    if hasattr(obj, '__annotations__'):
        return obj.__annotations__.copy()
    return {}


def object_to_dict(obj: Any) -> dict[str, Any]:
    if is_dataclass(obj):
        output = {}
        for class_field in fields(obj):  # noqa
            if class_field.init:
                # No need to handle nested classes
                output[class_field.name] = getattr(obj, class_field.name)
        return output
    if hasattr(obj, '__dict__'):
        return obj.__dict__.copy()
    return {}


def dict_to_object(cls: type[T], obj: dict[str, Any]) -> T:
    return cls(**obj)


def json_encoder(obj: Any) -> str | dict[str, Any]:
    if isinstance(obj, bytes):
        return 'base64:' + base64.b64encode(obj).decode()
    if output := object_to_dict(obj):
        output['_type'] = object_to_type_str(obj)
        return output
    # TODO: annotations? slots?
    raise TypeError(f'Object of type {type(obj).__name__} '
                    f'is not serializable')


def json_decoder(obj: dict[str, Any]) -> Any:
    for key, value in obj.items():
        if isinstance(value, str) and value.startswith('base64:'):
            obj[key] = base64.b64decode(value[7:])
    if (obj_type := obj.pop('_type', '')) and callable(cls := type_str_to_object(obj_type)):
        try:
            return dict_to_object(cls, obj)
        except TypeError:
            ...
    return obj


def json_encode_object(obj: Any) -> str:
    return 'json:' + json.dumps(obj, separators=(',', ':'), default=json_encoder)


def json_decode_object(s: str) -> Any:
    return json.loads(s[5:] if s.startswith('json:') else s, object_hook=json_decoder)


def get_subclasses(cls: type[T], contain_self: bool = True) -> Generator[type[T]]:
    if contain_self:
        yield cls
    for sub_cls in cls.__subclasses__():
        yield from get_subclasses(sub_cls)
