import base64
import builtins
import json
import sqlite3
from collections.abc import Mapping, Sequence, ValuesView
from contextlib import contextmanager
from dataclasses import fields, is_dataclass
from importlib import import_module
from types import ModuleType, NoneType
from typing import TypeAlias, Any

T_DB: TypeAlias = int | float | str | bytes | NoneType
MAP_DB: dict[type, str] = {
    # NoneType: 'NULL',
    int: 'INTEGER',
    float: 'REAL',
    str: 'TEXT',
    bytes: 'BLOB'
}


def _object_to_type_str(obj: Any) -> str:
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


def _type_str_to_object(type_str: str) -> ModuleType | type | None:
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


def _get_fields(obj: Any) -> dict[str, type]:
    if is_dataclass(obj):
        output = {}
        for field in fields(obj):  # noqa
            if field.init:
                if isinstance(field.type, str):
                    o_type = _type_str_to_object(field.type)
                    if isinstance(o_type, type):
                        output[field.name] = o_type
                else:
                    output[field.name] = field.type
        return output
    if hasattr(obj, '__annotations__'):
        return obj.__annotations__.copy()
    return {}


def _object_to_dict(obj: Any) -> dict[str, Any]:
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


def _dict_to_object(cls, obj: dict[str, Any]) -> Any:
    return cls(**obj)


def _json_encoder(obj: Any) -> str | dict[str, Any]:
    if isinstance(obj, bytes):
        return 'base64:' + base64.b64encode(obj).decode()
    if output := _object_to_dict(obj):
        output['_type'] = _object_to_type_str(obj)
        return output
    # TODO: annotations? slots?
    raise TypeError(f'Object of type {obj.__class__.__name__} '
                    f'is not serializable')


def _json_decoder(obj: dict[str, Any]) -> Any:
    for key, value in obj.items():
        if isinstance(value, str) and value.startswith('base64:'):
            obj[key] = base64.b64decode(value[7:])
    if (obj_type := obj.pop('_type', '')) and callable(cls := _type_str_to_object(obj_type)):
        try:
            return _dict_to_object(cls, obj)
        except TypeError:
            ...
    return obj


def _json_encode_object(obj) -> str:
    return 'json:' + json.dumps(obj, separators=(',', ':'), default=_json_encoder)


def _json_decode_object(s: str):
    return json.loads(s[5:] if s.startswith('json:') else s, object_hook=_json_decoder)


class Table:
    structure: type | Mapping[str, type]
    name: str = ''
    primary_key: str = ''
    database: 'Database | None' = None

    def __init__(self, structure: type | Mapping[str, type] | None = None,
                 name: str = '', primary_key: str = ''):
        if structure is not None:
            self.structure = structure
        elif not hasattr(self, 'structure'):
            raise ValueError('Table structure not defined')
        if name:
            self.name = name
        elif not self.name:
            self.name = self.__class__.__name__ if isinstance(self.structure, Mapping) else self.structure.__name__
        if primary_key:
            self.primary_key = primary_key

    @property
    def fields(self) -> dict[str, type]:
        return dict(self.structure) if isinstance(self.structure, Mapping) else _get_fields(self.structure)

    def sql_create(self) -> str:
        sql_col = ','.join(
            f"{_n} {MAP_DB.get(_t, 'TEXT')}{' PRIMARY KEY' if self.primary_key == _n else ''}"
            for _n, _t in self.fields.items()
        )
        return f'CREATE TABLE IF NOT EXISTS {self.name}({sql_col})'

    def sql_insert(self, use_key_name: bool = True) -> str:
        sql_col = ','.join(f':{_}' if use_key_name else '?' for _ in self.fields.keys())
        return f'INSERT INTO {self.name} VALUES({sql_col})'

    def sql_select(self, where: Sequence[str] = tuple(),
                   use_key_name: bool = True, use_primary_key: bool = True) -> str:
        if use_primary_key and self.primary_key and self.primary_key not in where:
            where = (self.primary_key, *where)
        sql_where = ' AND '.join(f'{_} = :{_}' if use_key_name else f'{_} = ?' for _ in where)
        return f'SELECT * FROM {self.name}' + (f' WHERE {sql_where}' if sql_where else '')

    def execute(self, sql: str, params: Any = tuple(), db: sqlite3.Connection | None = None) -> list:
        # Database
        if not isinstance(db, sqlite3.Connection):
            if isinstance(self.database, Database):
                db = self.database.db
            else:
                raise ValueError('No database selected')
        # Params
        if isinstance(params, Sequence | ValuesView):
            params = [_ if isinstance(_, T_DB) else _json_encode_object(_) for _ in params]
        else:
            if not isinstance(params, Mapping):
                params = _object_to_dict(params)
            params = {_k: _v if isinstance(_v, T_DB) else _json_encode_object(_v)
                      for _k, _v in params.items()}
        # Execute
        cursor = db.execute(sql, params)
        result_header = [_[0] for _ in cursor.description] if cursor.description else []
        output = []
        for result in cursor.fetchall():
            tmp: dict[str, Any] = dict(zip(
                result_header,
                (_json_decode_object(_) if isinstance(_, str) and _.startswith('json:') else _ for _ in result)
            ))
            output.append(tmp if isinstance(self.structure, Mapping) else _dict_to_object(self.structure, tmp))
        return output


class Database:
    _db: sqlite3.Connection
    _tables: list[Table]
    _connected: bool = False
    path: str = ':memory:'

    def __init__(self, path: str = ':memory:', tables: Sequence[Table] = tuple()):
        if path:
            self.path = path
        if tables:
            self._tables = [*tables]

    def connect(self) -> None:
        # Connect
        self._db = sqlite3.connect(self.path)
        # Create tables
        for table in self._tables:
            table.database = self
            self._db.execute(table.sql_create())
        self._connected = True

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def db(self) -> sqlite3.Connection:
        return self._db

    @property
    def tables(self) -> list[Table]:
        return self._tables

    @contextmanager
    def edit(self, table_name: str = '', commit: bool = True):
        if not self.connected:
            self.connect()
        result = [_ for _ in self._tables if _.name == table_name] if table_name else self._tables
        if not result:
            raise ValueError(f'No table found: {table_name}')
        try:
            yield result[0]
        finally:
            if commit:
                self.commit()

    def commit(self) -> None:
        self._db.commit()

    def close(self, save: bool = True) -> None:
        if save:
            self.commit()
        self._db.close()
        self._connected = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
