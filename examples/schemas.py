from pydantic import BaseModel, Field

from categories.schemas import ListCategoryPydantic


class ListExamplePydantic(BaseModel):
    id: int
    title: str = Field(max_length=255)
    age: int
    price: float
    description: str = Field(max_length=2000)
    category_id: int


class CreateExamplePydantic(BaseModel):
    title: str
    age: int = Field(gt=0)
    price: float = Field(gt=0)
    description: str
    category_id: int = Field(ge=1)


class Status(BaseModel):
    status_code: int = 200
    message: str = None
    details: str = None
