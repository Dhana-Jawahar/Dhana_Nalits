from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    isbn: str = Field(min_length=1, max_length=20)
    price: Decimal = Field(ge=0)
    quantity: int = Field(default=0, ge=0)


class BookUpdate(BookCreate):
    pass


class BookResponse(BookCreate):
    model_config = ConfigDict(from_attributes=True)

    bookid: int


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8)
    role: str = "user"


class UserResponse(BaseModel):
    userid: int
    username: str
    role: str