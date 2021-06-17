from enum import Enum

from sqlalchemy import Boolean, Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class Shops(Enum):
    oz = 'oz'
    gz = 'gz'
    hp = 'hp'


class Medicament(Base):
    __tablename__ = 'medicines'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    shop = Column(Enum(Shops), index=True)
    mnn = Column(String, index=True)
    manufacturer = Column(String, index=True)
    price = Column(Float)
    form = Column(String)
    doze = Column(String)
    number = Column(String)
    specs = Column(JSONB)
    descriptions = Column(JSONB)
