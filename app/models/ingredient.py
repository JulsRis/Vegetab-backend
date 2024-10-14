from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    amount = Column(Float)
    unit = Column(String)
    expiration_date = Column(Date)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="ingredients")
