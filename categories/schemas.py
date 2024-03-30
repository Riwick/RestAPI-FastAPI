from pydantic import BaseModel, Field


class ListCategoryPydantic(BaseModel):
    id: int
    title: str


class CreateCategoryPydantic(BaseModel):
    title: str = Field(max_length=50)
