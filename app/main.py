from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from app.db.database import get_db
from app.services.notification_service import schedule_expiration_check, store_fcm_token, check_expiring_ingredients
from app.services.recipe_service import process_recipe_link, search_recipes, get_recipe_details
from app.services.ingredient_service import get_ingredients, add_ingredient, update_ingredient, delete_ingredient
from app.schemas.token import FCMToken
from app.schemas.recipe import RecipeLink, Recipe
from app.schemas.ingredient import IngredientCreate, Ingredient
from app.services.image_recognition_service import identify_ingredient_from_image
from app.services.recipe_suggestion_service import get_recipe_suggestions

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://luxury-shortbread-cb9e7e.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(schedule_expiration_check, 'interval', hours=24, args=[next(get_db())])
scheduler.start()

@app.get("/")
async def root():
    return {"message": "Welcome to the Food App API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/store-fcm-token")
async def store_token(token: FCMToken, db: Session = Depends(get_db)):
    success = store_fcm_token(db, token.user_id, token.token)
    if success:
        return {"message": "FCM token stored successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/process-recipe-link", response_model=Recipe)
async def add_recipe_link(recipe_link: RecipeLink, db: Session = Depends(get_db)):
    recipe = process_recipe_link(db, recipe_link.user_id, recipe_link.url)
    if recipe:
        return recipe
    else:
        raise HTTPException(status_code=400, detail="Failed to process recipe link")

@app.get("/api/v1/ingredients", response_model=list[Ingredient])
async def fetch_ingredients(db: Session = Depends(get_db)):
    ingredients = get_ingredients(db)
    return ingredients

@app.post("/api/v1/ingredients", response_model=Ingredient)
async def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    return add_ingredient(db, ingredient)

@app.put("/api/v1/ingredients/{ingredient_id}", response_model=Ingredient)
async def update_ingredient_endpoint(ingredient_id: int, ingredient: IngredientCreate, db: Session = Depends(get_db)):
    updated_ingredient = update_ingredient(db, ingredient_id, ingredient)
    if updated_ingredient:
        return updated_ingredient
    raise HTTPException(status_code=404, detail="Ingredient not found")

@app.delete("/api/v1/ingredients/{ingredient_id}")
async def delete_ingredient_endpoint(ingredient_id: int, db: Session = Depends(get_db)):
    success = delete_ingredient(db, ingredient_id)
    if success:
        return {"message": "Ingredient deleted successfully"}
    raise HTTPException(status_code=404, detail="Ingredient not found")

@app.post("/api/v1/ingredients/upload", response_model=dict)
async def upload_ingredient_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()
        identified_ingredient = identify_ingredient_from_image(contents)
        return identified_ingredient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ingredients/confirm", response_model=Ingredient)
async def confirm_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    return add_ingredient(db, ingredient)

@app.get("/api/v1/recipe-suggestions")
async def get_recipe_suggestions_endpoint(db: Session = Depends(get_db)):
    ingredients = get_ingredients(db)
    suggestions = get_recipe_suggestions(ingredients)
    return suggestions

@app.post("/api/v1/trigger-expiration-check")
async def trigger_expiration_check(db: Session = Depends(get_db)):
    schedule_expiration_check(db)
    return {"message": "Expiration check triggered successfully"}

@app.get("/api/v1/expiring-ingredients")
async def get_expiring_ingredients(db: Session = Depends(get_db)):
    expiring_ingredients = check_expiring_ingredients(db)
    return {"expiring_ingredients": expiring_ingredients}

@app.get("/api/v1/search_recipes")
async def search_recipes_endpoint(query: str, ingredients: str, db: Session = Depends(get_db)):
    ingredient_list = ingredients.split(',')
    recipes = search_recipes(db, query, ingredient_list)
    return {"recipes": recipes}

@app.get("/api/v1/recipe/{recipe_id}")
async def get_recipe_details_endpoint(recipe_id: int, db: Session = Depends(get_db)):
    recipe = get_recipe_details(recipe_id)
    if recipe:
        return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")

@app.post("/api/v1/mark_cooked/{recipe_id}")
async def mark_recipe_cooked(recipe_id: int, db: Session = Depends(get_db)):
    # Implement logic to mark recipe as cooked
    # For now, we'll just return a success message
    return {"message": f"Recipe {recipe_id} marked as cooked"}

@app.post("/api/v1/save_favorite/{recipe_id}")
async def save_recipe_favorite(recipe_id: int, db: Session = Depends(get_db)):
    # Implement logic to save recipe as favorite
    # For now, we'll just return a success message
    return {"message": f"Recipe {recipe_id} saved as favorite"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
