from pydantic import BaseModel


class MedicamentBase(BaseModel):
    title: str
    shop: str
    mnn: str
    manufacturer: str
    price: float
    form: str
    doze: str
    number: str
    specs: list[dict]
    descriptions: list[dict]


class Medicament(MedicamentBase):
    id: int

    class Config:
        orm_mode = True
