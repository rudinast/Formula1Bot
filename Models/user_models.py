import datetime
from typing import Optional

from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    username: str = Field(index=True)
    password: str = Field(max_length=256, min_length=6)
    email: EmailStr
    created_at: datetime.datetime = datetime.datetime.now()
    is_seller: bool = False

class UserInput(SQLModel):
    username: str
    password: str = Field(max_length=256, min_length=6)
    password2: str
    email: EmailStr
    is_seller: bool = False

    @field_validator('password2')
    @classmethod
    def password_match(cls, v, values):
        if 'password' in values.data and v != values.data['password']:
            raise ValueError("passwords don't match")
        return v

class UserLogin(SQLModel):
    username: str
    password: str