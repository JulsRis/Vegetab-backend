from datetime import datetime, timedelta
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
from sqlalchemy.orm import Session
from app.models.ingredient import Ingredient
from app.models.user import User
import os

# Initialize Firebase Admin SDK
cred = credentials.Certificate("/home/ubuntu/food_app/backend/firebase_admin_sdk.json")
firebase_admin.initialize_app(cred)

def check_expiring_ingredients(db: Session):
    # Get all ingredients from the database
    ingredients = db.query(Ingredient).all()

    # Check each ingredient for expiration
    for ingredient in ingredients:
        if ingredient.expiration_date:
            if isinstance(ingredient.expiration_date, str):
                expiration_date = datetime.strptime(ingredient.expiration_date, "%Y-%m-%d").date()
            else:
                expiration_date = ingredient.expiration_date
            days_until_expiration = (expiration_date - datetime.now().date()).days

            if days_until_expiration <= 3:  # Notify if ingredient expires within 3 days
                send_expiration_notification(db, ingredient, days_until_expiration)

def send_expiration_notification(db: Session, ingredient: Ingredient, days_until_expiration: int):
    # Get the user associated with this ingredient
    user = db.query(User).filter(User.id == ingredient.user_id).first()

    if user and user.fcm_token:
        message = messaging.Message(
            notification=messaging.Notification(
                title='Ingredient Expiring Soon',
                body=f'{ingredient.name} will expire in {days_until_expiration} days.'
            ),
            token=user.fcm_token,
        )

        try:
            response = messaging.send(message)
            print('Successfully sent message:', response)
        except Exception as e:
            print('Error sending message:', str(e))

def store_fcm_token(db: Session, user_id: int, fcm_token: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.fcm_token = fcm_token
        db.commit()
        return True
    return False

# Function to schedule the expiration check (to be called periodically)
def schedule_expiration_check(db: Session):
    check_expiring_ingredients(db)
