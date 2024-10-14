from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    instructions = Column(String)
    ingredients = Column(String)  # Changed from ARRAY(String) to String
    image_url = Column(String)

    user = relationship("User", back_populates="recipes")
