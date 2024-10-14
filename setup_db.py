from app.db.database import Base, engine
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.user import User

def setup_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    setup_database()
