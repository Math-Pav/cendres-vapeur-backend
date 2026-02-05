from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str
    password: str
    avatar_url: str | None = None
    biography: str | None = None

class UserCreate(UserBase):
    pass

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    avatar_url: str | None = None
    biography: str | None = None

    class Config:
        from_attributes = True

