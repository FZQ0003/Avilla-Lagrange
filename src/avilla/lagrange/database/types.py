from datetime import datetime

from graia.amnesia.builtins.sqla.model import _NAMING_CONVENTION, Base as _Base  # noqa
from sqlalchemy import BIGINT, TEXT, TypeDecorator, MetaData

from ..utils.misc import json_encode_object, json_decode_object


# Do not affect existing Base
class Base(_Base):
    __abstract__ = True
    metadata = MetaData(naming_convention=_NAMING_CONVENTION)


class BigTimestamp(TypeDecorator[datetime]):
    impl = BIGINT

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime):
            return int(value.timestamp())
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return datetime.fromtimestamp(value)
        return value


class JsonText(TypeDecorator[object]):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json_encode_object(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json_decode_object(value)
        return value
