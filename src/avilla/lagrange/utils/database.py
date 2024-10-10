import sqlite3
from collections.abc import Mapping, Sequence, ValuesView
from contextlib import contextmanager
from types import NoneType
from typing import TypeAlias, Any

from .misc import get_fields, object_to_dict, dict_to_object, json_encode_object, json_decode_object

T_DB: TypeAlias = int | float | str | bytes | NoneType
MAP_DB: dict[type, str] = {
    # NoneType: 'NULL',
    int: 'INTEGER',
    float: 'REAL',
    str: 'TEXT',
    bytes: 'BLOB'
}


class Table:
    structure: type | Mapping[str, type]
    name: str = ''
    primary_key: str = ''  # TODO: more columns?
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
            self.name = type(self).__name__ if isinstance(self.structure, Mapping) else self.structure.__name__
        if primary_key:
            self.primary_key = primary_key

    @property
    def fields(self) -> dict[str, type]:
        return dict(self.structure) if isinstance(self.structure, Mapping) else get_fields(self.structure)

    def sql_create(self) -> str:
        sql_col = ','.join(
            f"{_n} {MAP_DB.get(_t, 'TEXT')}"
            # f"{' UNIQUE' if _n in self.unique_keys else ''}"
            f"{' PRIMARY KEY' if self.primary_key == _n else ''}"
            for _n, _t in self.fields.items()
        )
        return f'CREATE TABLE IF NOT EXISTS {self.name}({sql_col})'

    def sql_insert(self, use_key_name: bool = True, replace: bool = True) -> str:
        sql_col = ','.join(f':{_}' if use_key_name else '?' for _ in self.fields.keys())
        return f"INSERT OR {'REPLACE' if replace else 'IGNORE'} INTO {self.name} VALUES({sql_col})"

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
            params = [_ if isinstance(_, T_DB) else json_encode_object(_) for _ in params]
        else:
            if not isinstance(params, Mapping):
                params = object_to_dict(params)
            params = {_k: _v if isinstance(_v, T_DB) else json_encode_object(_v)
                      for _k, _v in params.items()}
        # Execute
        cursor = db.execute(sql, params)
        result_header = [_[0] for _ in cursor.description] if cursor.description else []
        output = []
        for result in cursor.fetchall():
            tmp: dict[str, Any] = dict(zip(
                result_header,
                (json_decode_object(_) if isinstance(_, str) and _.startswith('json:') else _ for _ in result)
            ))
            output.append(tmp if isinstance(self.structure, Mapping) else dict_to_object(self.structure, tmp))
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

    def get_table(self, table_name: str = '') -> Table:
        result = [_ for _ in self._tables if _.name == table_name] if table_name else self._tables
        if result:
            return result[0]
        raise ValueError(f'No table found: {table_name}')

    @contextmanager
    def edit(self, table_name: str = '', commit: bool = True):
        if not self._connected:
            self.connect()
        table = self.get_table(table_name)
        try:
            yield table
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
