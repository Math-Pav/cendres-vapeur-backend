from pydantic import BaseModel
from datetime import date

class ShiftNoteBase(BaseModel):
    order_id: int
    date: date
    content: str
    shift_type: str

class ShiftNoteCreate(ShiftNoteBase):
    pass

class ShiftNoteOut(ShiftNoteBase):

    class Config:
        from_attributes = True
