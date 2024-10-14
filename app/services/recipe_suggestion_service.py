import random
from typing import List
from app.models.ingredient import Ingredient

def get_recipe_suggestions(ingredients: List[Ingredient], number: int = 5) -> List[dict]:
    # Mock recipe suggestions
    mock_recipes = [
        {"id": 1, "title": "Pasta Primavera", "image": "https://example.com/pasta.jpg"},
        {"id": 2, "title": "Chicken Stir Fry", "image": "https://example.com/stirfry.jpg"},
        {"id": 3, "title": "Vegetable Soup", "image": "https://example.com/soup.jpg"},
        {"id": 4, "title": "Grilled Salmon", "image": "https://example.com/salmon.jpg"},
        {"id": 5, "title": "Caesar Salad", "image": "https://example.com/salad.jpg"},
        {"id": 6, "title": "Beef Tacos", "image": "https://example.com/tacos.jpg"},
        {"id": 7, "title": "Mushroom Risotto", "image": "https://example.com/risotto.jpg"},
        {"id": 8, "title": "Vegetable Curry", "image": "https://example.com/curry.jpg"},
    ]

    # Randomly select 'number' of recipes
    selected_recipes = random.sample(mock_recipes, min(number, len(mock_recipes)))

    return [
        {
            "id": recipe["id"],
            "title": recipe["title"],
            "image": recipe["image"],
            "usedIngredientCount": random.randint(1, len(ingredients)),
            "missedIngredientCount": random.randint(0, 3)
        }
        for recipe in selected_recipes
    ]
