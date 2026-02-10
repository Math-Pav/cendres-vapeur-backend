from pydantic import BaseModel
from datetime import date

class ColonyEventBase(BaseModel):
    title: str
    date: date
    severity: str

class ColonyEventCreate(ColonyEventBase):
    pass

class ColonyEventOut(ColonyEventBase):
    id: int

    class Config:
        from_attributes = True