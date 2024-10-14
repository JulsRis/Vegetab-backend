from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate, IngredientResponse
from typing import List, Optional
import cv2
import numpy as np
from PIL import Image
import io
import tensorflow as tf
from datetime import datetime, timedelta
import requests

router = APIRouter()

# Load a pre-trained model for image classification
model = tf.keras.applications.MobileNetV2(weights='imagenet')

@router.post("/ingredients/", response_model=IngredientResponse)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = Ingredient(**ingredient.dict())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@router.get("/ingredients/", response_model=List[IngredientResponse])
def read_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ingredients = db.query(Ingredient).offset(skip).limit(limit).all()
    return ingredients

@router.post("/ingredients/recognize/")
async def recognize_ingredient(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    image = image.resize((224, 224))  # Resize image to match model input size
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_array = tf.expand_dims(image_array, 0)  # Create batch axis
    image_array = tf.keras.applications.mobilenet_v2.preprocess_input(image_array)

    predictions = model.predict(image_array)
    decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)[0]

    recognized_ingredient = decoded_predictions[0][1]  # Get the class name
    confidence = float(decoded_predictions[0][2])  # Get the confidence score

    return {"recognized_ingredient": recognized_ingredient, "confidence": confidence}

@router.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(ingredient_id: int, ingredient: IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    for key, value in ingredient.dict().items():
        setattr(db_ingredient, key, value)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@router.delete("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(db_ingredient)
    db.commit()
    return db_ingredient

@router.get("/ingredients/expiring/", response_model=List[IngredientResponse])
def get_expiring_ingredients(days: int = 3, db: Session = Depends(get_db)):
    expiration_date = datetime.now() + timedelta(days=days)
    expiring_ingredients = db.query(Ingredient).filter(Ingredient.expiration_date <= expiration_date).all()
    return expiring_ingredients

@router.post("/ingredients/confirm/")
def confirm_ingredient(ingredient_id: int, confirmed_name: str, db: Session = Depends(get_db)):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db_ingredient.name = confirmed_name
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@router.post("/ingredients/use/")
def use_ingredient(ingredient_id: int, amount_used: float, db: Session = Depends(get_db)):
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if db_ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db_ingredient.amount -= amount_used
    if db_ingredient.amount <= 0:
        db.delete(db_ingredient)
    db.commit()
    return {"message": "Ingredient updated or removed"}

@router.get("/recipes/suggestions/")
def get_recipe_suggestions(db: Session = Depends(get_db)):
    ingredients = db.query(Ingredient).all()
    ingredient_names = [ingredient.name for ingredient in ingredients]

    api_key = "YOUR_SPOONACULAR_API_KEY"  # Replace with actual API key
    base_url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ",".join(ingredient_names),
        "number": 5,
        "apiKey": api_key
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch recipe suggestions")

@router.get("/recipes/{recipe_id}")
def get_recipe_details(recipe_id: int):
    api_key = "YOUR_SPOONACULAR_API_KEY"  # Replace with actual API key
    base_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": api_key}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail="Failed to fetch recipe details")

@router.post("/recipes/mark-cooked/{recipe_id}")
def mark_recipe_cooked(recipe_id: int, db: Session = Depends(get_db)):
    # TODO: Implement logic to mark recipe as cooked and update ingredient quantities
    return {"message": f"Recipe {recipe_id} marked as cooked"}

@router.post("/recipes/favorite/{recipe_id}")
def favorite_recipe(recipe_id: int, db: Session = Depends(get_db)):
    # TODO: Implement logic to save recipe as favorite
    return {"message": f"Recipe {recipe_id} saved as favorite"}

@router.post("/recipes/parse-url")
def parse_recipe_url(url: str):
    api_key = "YOUR_SPOONACULAR_API_KEY"  # Replace with actual API key
    base_url = "https://api.spoonacular.com/recipes/extract"
    params = {"apiKey": api_key, "url": url}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail="Failed to parse recipe URL")

def send_push_notification(user_id: int, message: str):
    # TODO: Implement actual push notification logic
    print(f"Sending push notification to user {user_id}: {message}")

@router.post("/ingredients/check-expiration/")
def check_expiration(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    expiring_ingredients = get_expiring_ingredients(days=3, db=db)
    for ingredient in expiring_ingredients:
        message = f"Your {ingredient.name} is expiring soon!"
        background_tasks.add_task(send_push_notification, user_id=1, message=message)
    return {"message": "Expiration check completed"}

# TODO: Implement recipe suggestions based on available ingredients
# TODO: Implement push notifications for expiring ingredients
