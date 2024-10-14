import tensorflow as tf
import numpy as np
from PIL import Image
import io

# Load a pre-trained MobileNetV2 model
model = tf.keras.applications.MobileNetV2(weights='imagenet')

def identify_ingredient_from_image(image_data):
    # Convert the image data to a PIL Image
    image = Image.open(io.BytesIO(image_data))

    # Preprocess the image
    image = image.resize((224, 224))
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_array = tf.keras.applications.mobilenet_v2.preprocess_input(image_array)
    image_array = np.expand_dims(image_array, axis=0)

    # Make a prediction
    predictions = model.predict(image_array)
    decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)[0]

    # Return the top prediction
    _, ingredient_name, confidence = decoded_predictions[0]

    return {
        "name": ingredient_name.replace('_', ' ').title(),
        "confidence": float(confidence),
        "amount": 1,
        "unit": "piece",
        "expiration_date": None
    }
