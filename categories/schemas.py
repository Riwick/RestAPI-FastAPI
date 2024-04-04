from pydantic import BaseModel, Field


class ListCategoryPydantic(BaseModel):
    """Схема по которой выводятся категории"""
    id: int
    title: str


class CreateCategoryPydantic(BaseModel):
    """Схема по которой создаются категории"""
    title: str = Field(max_length=50)
