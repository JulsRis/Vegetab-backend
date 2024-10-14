from pydantic import BaseModel
from datetime import date

class IngredientBase(BaseModel):
    name: str
    amount: float
    unit: str | None = None
    expiration_date: date | None = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    amount: float | None = None
    expiration_date: date | None = None

class Ingredient(IngredientBase):
    id: int

    class Config:
        from_attributes = True
