from pydantic import BaseModel
from typing import List, Optional

class RecipeBase(BaseModel):
    title: str
    image: Optional[str] = None
    servings: Optional[int] = None
    ready_in_minutes: Optional[int] = None
    instructions: str
    ingredients: List[str]

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class RecipeSearch(BaseModel):
    query: str

class RecipeLink(BaseModel):
    user_id: int
    url: str
