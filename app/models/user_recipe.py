from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserRecipe(Base):
    __tablename__ = "user_recipes"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, index=True)
    last_cooked = Column(DateTime, nullable=True)
    cook_count = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)

    # Add any additional fields as needed
