import os
from collections import Iterable
from dataclasses import dataclass, asdict
from enum import Enum
from functools import cached_property

import jq
import pymongo
from pymongo.database import Database
from sqlalchemy import create_engine, MetaData, Column, String, Integer, Table, Float
from sqlalchemy.dialects.postgresql import JSONB

PGSQL_URI = os.environ['PGSQL_URI']
MONGO_URI = os.environ['MONGO_URI']
MONGO_DATABASE = os.environ['MONGO_DATABASE']

engine = create_engine(PGSQL_URI)
meta = MetaData()


class Shops(Enum):
    oz = 'oz'
    gz = 'gz'
    hp = 'hp'


medicines = Table(
    'medicines', meta,
    Column('id', Integer, primary_key=True),
    Column('title', String),
    Column('shop', Enum(Shops)),
    Column('price', Float),
    Column('mnn', String),
    Column('manufacturer', String),
    Column('form', String),
    Column('doze', String),
    Column('number', String),
    Column('specs', JSONB),
    Column('descriptions', JSONB),
)


@dataclass
class Medicament:
    href: str
    title: str
    shop: str
    price: float
    mnn: str
    manufacturer: str
    form: str
    doze: str
    number: str
    specs: list[dict]
    descriptions: list[dict]


class Unifier:
    _name: str

    def __init__(self, name: str):
        self._name = name

    def process(self):
        meta.create_all(engine)

        with engine.connect() as conn:
            for med in map(self._transform, self._documents):
                ins = medicines.insert().values(**asdict(med))
                conn.execute(ins)

    @property
    def _documents(self) -> Iterable[dict]:
        with pymongo.MongoClient(MONGO_URI) as client:  # type: pymongo.MongoClient
            db: Database = client[MONGO_DATABASE]
            collection_name: str = max(cn for cn in db.list_collection_names() if cn.startswith(self._name))

            yield from db[collection_name]

    @cached_property
    def _jq_query(self) -> str:
        with open(f'farma_unifier/files/queries/{self._name}.jq', 'r', encoding='utf-8') as file:
            return file.read()

    def _transform(self, document: dict) -> Medicament:
        return jq.compile(self._jq_query).input(document).first()
