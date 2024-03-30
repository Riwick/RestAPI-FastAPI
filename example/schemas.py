from decimal import Decimal

from pydantic import BaseModel, Field


class ListCategoryPydantic(BaseModel):
    id: int
    title: str


class CreateCategoryPydantic(BaseModel):
    title: str


class ListExamplePydantic(BaseModel):
    id: int
    title: str
    age: int = Field(gt=0)
    price: float = Field(gt=0)
    description: str
    category_id: int


class CreateExamplePydantic(BaseModel):
    title: str
    age: int = Field(gt=0)
    price: float = Field(gt=0)
    description: str
    category_id: int

