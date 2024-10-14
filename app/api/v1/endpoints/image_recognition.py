from fastapi import APIRouter, File, UploadFile, HTTPException
from google.cloud import vision
import os
from core.config import settings
from typing import List
import re
from datetime import datetime, timedelta

router = APIRouter()

client = vision.ImageAnnotatorClient()

@router.post("/identify_ingredient")
async def identify_ingredient(file: UploadFile = File(...)):
    try:
        content = await file.read()
        image = vision.Image(content=content)

        # Perform text detection
        text_response = client.text_detection(image=image)
        texts = text_response.text_annotations

        # Perform label detection
        label_response = client.label_detection(image=image)
        labels = label_response.label_annotations

        # Extract information
        ingredients = extract_ingredients(texts, labels)

        if ingredients:
            return {"ingredients": ingredients, "status": "pending_confirmation"}
        else:
            return {"message": "No food ingredients detected in the image", "status": "no_ingredients"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_ingredients(texts, labels):
    ingredients = []
    text_content = texts[0].description if texts else ""

    # Extract ingredients from labels
    food_labels = [label.description for label in labels if label.score > 0.7 and is_food_related(label.description)]

    for label in food_labels:
        ingredient = {
            "name": label,
            "amount": extract_amount(text_content, label),
            "expirationDate": extract_expiration_date(text_content)
        }
        ingredients.append(ingredient)

    return ingredients

def extract_amount(text, ingredient):
    # Simple regex to find amount near the ingredient name
    pattern = r'(\d+(\.\d+)?)\s*(g|kg|ml|l|oz|lb|cup|tbsp|tsp)\s*' + re.escape(ingredient)
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else ""

def extract_expiration_date(text):
    # Simple regex to find dates in common formats
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
        r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY or DD-MM-YYYY
        r'\d{4}-\d{2}-\d{2}',        # YYYY-MM-DD
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}'  # Month DD, YYYY
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                date = datetime.strptime(match.group(0), "%Y-%m-%d")
                return date.strftime("%Y-%m-%d")
            except ValueError:
                pass  # If parsing fails, try the next pattern

    return ""

def is_food_related(label: str) -> bool:
    # This is a simple check. You might want to use a more comprehensive list or API for better accuracy.
    food_related_words = ['food', 'ingredient', 'fruit', 'vegetable', 'meat', 'dairy', 'grain', 'spice', 'herb']
    return any(word in label.lower() for word in food_related_words)

@router.post("/confirm_ingredients")
async def confirm_ingredients(ingredients: List[dict]):
    # Here we would typically save the confirmed ingredients to the database
    return {"confirmed_ingredients": ingredients, "status": "confirmed"}

@router.post("/amend_ingredients")
async def amend_ingredients(original: List[dict], amended: List[dict]):
    # Here we would typically update the ingredients in the database
    return {"original_ingredients": original, "amended_ingredients": amended, "status": "amended"}
