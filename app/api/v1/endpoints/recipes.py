from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import requests
from datetime import datetime

from db.database import get_db
from models.ingredient import Ingredient
from models.user_recipe import UserRecipe
from schemas.recipe import Recipe, RecipeSearch
from schemas.user_recipe import UserRecipe as UserRecipeSchema

router = APIRouter()

SPOONACULAR_API_KEY = "YOUR_SPOONACULAR_API_KEY"  # Replace with actual API key
SPOONACULAR_BASE_URL = "https://api.spoonacular.com"

@router.get("/search", response_model=List[Recipe])
def search_recipes(query: str, db: Session = Depends(get_db)):
    url = f"{SPOONACULAR_BASE_URL}/recipes/complexSearch"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "query": query,
        "number": 10,
        "addRecipeInformation": True,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch recipes")
    return response.json()["results"]

@router.get("/by_ingredients", response_model=List[Recipe])
def get_recipes_by_ingredients(db: Session = Depends(get_db)):
    ingredients = db.query(Ingredient).all()
    ingredient_names = [ingredient.name for ingredient in ingredients]

    url = f"{SPOONACULAR_BASE_URL}/recipes/findByIngredients"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "ingredients": ",".join(ingredient_names),
        "number": 10,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch recipes")
    return response.json()

@router.get("/{recipe_id}/instructions", response_model=str)
def get_recipe_instructions(recipe_id: int):
    url = f"{SPOONACULAR_BASE_URL}/recipes/{recipe_id}/analyzedInstructions"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch recipe instructions")
    instructions = response.json()
    return "\n".join([step["step"] for step in instructions[0]["steps"]])

@router.get("/{recipe_id}/missing_ingredients", response_model=List[str])
def get_missing_ingredients(recipe_id: int, db: Session = Depends(get_db)):
    url = f"{SPOONACULAR_BASE_URL}/recipes/{recipe_id}/ingredientWidget.json"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch recipe ingredients")

    recipe_ingredients = response.json()["ingredients"]
    recipe_ingredient_names = [ingredient["name"] for ingredient in recipe_ingredients]

    available_ingredients = db.query(Ingredient).all()
    available_ingredient_names = [ingredient.name for ingredient in available_ingredients]

    missing_ingredients = [ingredient for ingredient in recipe_ingredient_names if ingredient not in available_ingredient_names]
    return missing_ingredients

@router.post("/{recipe_id}/mark_cooked", response_model=UserRecipeSchema)
def mark_recipe_as_cooked(recipe_id: int, db: Session = Depends(get_db)):
    user_recipe = db.query(UserRecipe).filter(UserRecipe.recipe_id == recipe_id).first()
    if user_recipe:
        user_recipe.cook_count += 1
        user_recipe.last_cooked = datetime.utcnow()
    else:
        user_recipe = UserRecipe(recipe_id=recipe_id, cook_count=1, last_cooked=datetime.utcnow())
    db.add(user_recipe)
    db.commit()
    db.refresh(user_recipe)
    return user_recipe

@router.post("/{recipe_id}/favorite", response_model=UserRecipeSchema)
def save_favorite_recipe(recipe_id: int, db: Session = Depends(get_db)):
    user_recipe = db.query(UserRecipe).filter(UserRecipe.recipe_id == recipe_id).first()
    if user_recipe:
        user_recipe.is_favorite = True
    else:
        user_recipe = UserRecipe(recipe_id=recipe_id, is_favorite=True)
    db.add(user_recipe)
    db.commit()
    db.refresh(user_recipe)
    return user_recipe

@router.delete("/{recipe_id}/favorite", response_model=UserRecipeSchema)
def remove_favorite_recipe(recipe_id: int, db: Session = Depends(get_db)):
    user_recipe = db.query(UserRecipe).filter(UserRecipe.recipe_id == recipe_id).first()
    if user_recipe:
        user_recipe.is_favorite = False
        db.add(user_recipe)
        db.commit()
        db.refresh(user_recipe)
        return user_recipe
    raise HTTPException(status_code=404, detail="Recipe not found in favorites")
