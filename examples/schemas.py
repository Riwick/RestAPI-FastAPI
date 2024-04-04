from pydantic import BaseModel, Field


class ListExamplePydantic(BaseModel):
    """Схема по которой выводятся объекты класса Example """
    id: int
    title: str = Field(max_length=255)
    age: int
    price: float
    description: str = Field(max_length=2000)
    category_id: int


class CreateExamplePydantic(BaseModel):
    """Схема по которой создаются объекты класса Example"""
    title: str
    age: int = Field(gt=0)
    price: float = Field(gt=0)
    description: str
    category_id: int = Field(ge=1)


class Status(BaseModel):
    """Схема ответа после успешного удаления объекта класса Example"""
    status_code: int = 200
    message: str = None
    details: str = None
