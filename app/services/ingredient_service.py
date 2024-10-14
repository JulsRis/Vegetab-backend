from sqlalchemy.orm import Session
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate

def get_ingredients(db: Session):
    return db.query(Ingredient).all()

def add_ingredient(db: Session, ingredient: IngredientCreate):
    db_ingredient = Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

def update_ingredient(db: Session, ingredient_id: int, ingredient: IngredientCreate):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if db_ingredient:
        for key, value in ingredient.dict().items():
            setattr(db_ingredient, key, value)
        db.commit()
        db.refresh(db_ingredient)
        return db_ingredient
    return None

def delete_ingredient(db: Session, ingredient_id: int):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if db_ingredient:
        db.delete(db_ingredient)
        db.commit()
        return True
    return False
