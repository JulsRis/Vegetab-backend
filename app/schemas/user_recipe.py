from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserRecipeBase(BaseModel):
    recipe_id: int
    user_id: int
    title: str

class UserRecipeCreate(UserRecipeBase):
    pass

class UserRecipeUpdate(BaseModel):
    last_cooked: Optional[datetime] = None
    cook_count: Optional[int] = None
    is_favorite: Optional[bool] = None

class UserRecipe(UserRecipeBase):
    id: int
    last_cooked: Optional[datetime]
    cook_count: int
    is_favorite: bool

    class Config:
        orm_mode = True
