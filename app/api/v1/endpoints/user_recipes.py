from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from db.database import get_db
from models.user_recipe import UserRecipe
from schemas.user_recipe import UserRecipeCreate, UserRecipeUpdate, UserRecipe as UserRecipeSchema

router = APIRouter()

@router.post("/cooked", response_model=UserRecipeSchema)
def mark_recipe_as_cooked(recipe: UserRecipeCreate, db: Session = Depends(get_db)):
    existing_recipe = db.query(UserRecipe).filter(UserRecipe.id == recipe.id).first()
    if existing_recipe:
        existing_recipe.cook_count += 1
        existing_recipe.last_cooked = datetime.utcnow()
        db.add(existing_recipe)
    else:
        new_recipe = UserRecipe(**recipe.dict(), last_cooked=datetime.utcnow(), cook_count=1)
        db.add(new_recipe)
    db.commit()
    db.refresh(existing_recipe if existing_recipe else new_recipe)
    return existing_recipe if existing_recipe else new_recipe

@router.get("/cooked", response_model=List[UserRecipeSchema])
def get_cooked_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recipes = db.query(UserRecipe).filter(UserRecipe.last_cooked.isnot(None)).offset(skip).limit(limit).all()
    return recipes

@router.post("/favorite", response_model=UserRecipeSchema)
def save_favorite_recipe(recipe: UserRecipeCreate, db: Session = Depends(get_db)):
    db_recipe = UserRecipe(**recipe.dict(), is_favorite=True)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

@router.get("/favorite", response_model=List[UserRecipeSchema])
def get_favorite_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recipes = db.query(UserRecipe).filter(UserRecipe.is_favorite == True).offset(skip).limit(limit).all()
    return recipes

@router.put("/{recipe_id}", response_model=UserRecipeSchema)
def update_user_recipe(recipe_id: int, recipe: UserRecipeUpdate, db: Session = Depends(get_db)):
    db_recipe = db.query(UserRecipe).filter(UserRecipe.id == recipe_id).first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    update_data = recipe.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_recipe, key, value)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe
