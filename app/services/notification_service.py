from datetime import datetime, timedelta
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
from sqlalchemy.orm import Session
from app.models.ingredient import Ingredient
from app.models.user import User
import os
import json

# Initialize Firebase Admin SDK
firebase_creds = os.getenv('FIREBASE_CREDENTIALS')
firebase_initialized = False

if firebase_creds:
    try:
        cred = credentials.Certificate(json.loads(firebase_creds))
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
    except Exception as e:
        print(f"Warning: Failed to initialize Firebase: {str(e)}")
else:
    print("Warning: Firebase credentials not found. Notifications will not work.")

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
    if not firebase_initialized:
        print(f"Notification would be sent: {ingredient.name} will expire in {days_until_expiration} days.")
        return

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
