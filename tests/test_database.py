import json
import sqlite3
from dataclasses import dataclass

from avilla.lagrange.utils.database import Table, Database


@dataclass
class SampleData:
    a: int
    b: str
    c: bytes


@dataclass
class SampleTableData:
    id: int
    name: str
    data_a: dict[str, str]
    data_b: list[SampleData]


class SampleTableA(Table):
    structure = {
        'id': int,
        'name': str,
        'data': bytes
    }
    primary_key = 'id'


class TestTable:
    table_a = SampleTableA()
    table_b = Table(
        structure=SampleTableData,
        name='SampleTableB',
        primary_key='id'
    )

    def test_table_attr(self):
        assert self.table_a.structure == {'id': int, 'name': str, 'data': bytes}
        assert self.table_a.name == 'SampleTableA'
        assert self.table_b.structure == SampleTableData
        assert self.table_b.name == 'SampleTableB'
        assert self.table_a.primary_key == self.table_b.primary_key == 'id'
        assert self.table_a.database is self.table_b.database is None

    def test_table_fields(self):
        assert self.table_a.fields == self.table_a.structure
        assert self.table_b.fields == SampleTableData.__annotations__

    def test_table_sql_create(self):
        test_str_a = self.table_a.sql_create()
        assert test_str_a.startswith('CREATE TABLE IF NOT EXISTS SampleTableA(')
        assert test_str_a.endswith(')')
        assert test_str_a[test_str_a.find('(') + 1:-1].split(',') == [
            'id INTEGER PRIMARY KEY',
            'name TEXT',
            'data BLOB'
        ]
        test_str_b = self.table_b.sql_create()
        assert test_str_b.startswith('CREATE TABLE IF NOT EXISTS SampleTableB(')
        assert test_str_b.endswith(')')
        assert test_str_b[test_str_b.find('(') + 1:-1].split(',') == [
            'id INTEGER PRIMARY KEY',
            'name TEXT',
            'data_a TEXT',
            'data_b TEXT'
        ]

    def test_table_sql_insert(self):
        test_str = self.table_a.sql_insert()
        assert test_str.startswith('INSERT INTO SampleTableA VALUES(')
        assert test_str.endswith(')')
        assert test_str[test_str.find('(') + 1:-1] == ':id,:name,:data'
        test_str = self.table_a.sql_insert(use_key_name=False)
        assert test_str[test_str.find('(') + 1:-1] == '?,?,?'

    def test_table_sql_select(self):
        assert self.table_b.sql_select() == 'SELECT * FROM SampleTableB WHERE id = :id'
        assert self.table_b.sql_select(use_key_name=False) == 'SELECT * FROM SampleTableB WHERE id = ?'
        assert self.table_b.sql_select(use_primary_key=False) == 'SELECT * FROM SampleTableB'
        assert self.table_b.sql_select(
            where=['name', 'id']
        ) == 'SELECT * FROM SampleTableB WHERE name = :name AND id = :id'
        assert self.table_b.sql_select(
            where=['name']
        ) == 'SELECT * FROM SampleTableB WHERE id = :id AND name = :name'
        assert self.table_b.sql_select(
            where=['name'], use_primary_key=False
        ) == 'SELECT * FROM SampleTableB WHERE name = :name'
        assert Table({}).sql_select() == 'SELECT * FROM Table'

    def test_execute_a(self):
        database = sqlite3.connect(':memory:')
        try:
            self.table_a.execute(self.table_a.sql_create(), db=database)
            assert ('SampleTableA',) in database.execute('SELECT name FROM sqlite_schema').fetchall()
            test_data_1 = {'id': 114514, 'name': 'senpai', 'data': b'1919810'}
            test_data_2 = {'id': 415411, 'name': 'iapnes', 'data': b'0189191'}
            self.table_a.execute(
                self.table_a.sql_insert(),
                test_data_1,
                db=database
            )
            self.table_a.execute(
                self.table_a.sql_insert(use_key_name=False),
                test_data_2.values(),
                db=database
            )
            assert database.execute(
                'SELECT * FROM SampleTableA WHERE id = 114514'
            ).fetchall() == [tuple(test_data_1.values())]
            assert self.table_a.execute(
                self.table_a.sql_select(),
                {'id': 114514},
                db=database
            ) == [test_data_1]
            assert self.table_a.execute(
                self.table_a.sql_select(use_key_name=False),
                (114514,),
                db=database
            ) == [test_data_1]
            assert self.table_a.execute(
                self.table_a.sql_select(where=['name'], use_primary_key=False),
                test_data_2,
                db=database
            ) == [test_data_2]
            assert self.table_a.execute(
                self.table_a.sql_select(use_primary_key=False),
                db=database
            ) == [test_data_1, test_data_2]
        finally:
            database.close()

    def test_execute_b(self):
        database = sqlite3.connect(':memory:')
        try:
            self.table_b.execute(self.table_b.sql_create(), db=database)
            assert ('SampleTableB',) in database.execute('SELECT name FROM sqlite_schema').fetchall()
            test_data = SampleTableData(id=123, name='test', data_a={'114': '514'}, data_b=[
                SampleData(a=1, b='a', c=b'x'),
                SampleData(a=2, b='b', c=b'y'),
                SampleData(a=3, b='c', c=b'z')
            ])
            self.table_b.execute(
                self.table_b.sql_insert(),
                test_data,
                db=database
            )
            test_select = database.execute('SELECT * FROM SampleTableB WHERE id = 123').fetchone()
            assert test_select[0:2] == (123, 'test')
            assert test_select[2] == 'json:{"114":"514"}'
            assert json.loads(test_select[3][5:])[0] == {
                '_type': 'test_database.SampleData',
                'a': 1,
                'b': 'a',
                'c': 'base64:eA=='
            }
            assert self.table_b.execute(
                self.table_b.sql_select(),
                {'id': 123},
                db=database
            ) == [test_data]
        finally:
            database.close()


class TestDatabase:
    database: Database

    def setup_class(self):
        self.database = Database(tables=[SampleTableA()])
        self.database.connect()

    def teardown_class(self):
        self.database.close(save=False)

    def test_edit(self):
        with self.database.edit(table_name='SampleTableA', commit=False) as t:
            t: Table
            t.execute(t.sql_create())
            test_data_list = [
                {'id': 114514, 'name': 'senpai', 'data': b'1919810'},
                {'id': 415411, 'name': 'iapnes', 'data': b'0189191'}
            ]
            for data in test_data_list:
                t.execute(t.sql_insert(), data)
            assert t.execute(t.sql_select(), {'id': 415411}) == [test_data_list[1]]
