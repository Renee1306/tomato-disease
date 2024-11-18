from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
from dotenv import load_dotenv
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from pymongo import MongoClient
import datetime

# Load environment variables from .env file
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Get the MongoDB URI from the .env file
mongodb_uri = os.getenv("MONGODB_URI")

# Establish the connection
client = MongoClient(mongodb_uri)

db = client["predictions"]  
collection = db["tomato"]  

class SEBlock(layers.Layer):
    def __init__(self, filters, reduction=16, **kwargs):  
        super(SEBlock, self).__init__(**kwargs) 
        self.global_avg_pool = layers.GlobalAveragePooling2D()
        self.dense1 = layers.Dense(filters // reduction, activation='relu')
        self.dense2 = layers.Dense(filters, activation='sigmoid')

    def call(self, inputs):
        se = self.global_avg_pool(inputs)
        se = self.dense1(se)
        se = self.dense2(se)
        se = layers.Reshape((1, 1, se.shape[-1]))(se)  
        return inputs * se  


# Load the pre-trained CNN model for image classification
cnn_model = tf.keras.models.load_model("cnn_model.h5", custom_objects={'SEBlock': SEBlock})

IMG_SIZE = (256, 256)  # Adjust according to your model input size

# Define the class names (use the ones from your dataset)
class_names = [
    'Bacterial Spot', 
    'Early Blight', 
    'Late Blight',
    'Leaf Mold', 
    'Septoria Leaf Spot',
    'Two Spotted Spider Mite', 
    'Target Spot',
    'Tomato Yellow Leaf Curl Virus', 
    'Tomato Mosaic Virus',
    'Healthy'
]

# Helper function to preprocess image
def preprocess_image(img_path, img_size):
    img = image.load_img(img_path, target_size=img_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Normalize to [0, 1]
    return img_array


# Create the Generative AI model for treatment suggestions
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

genai_model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/diagnosis')
def diagnosis():
    return render_template('diagnosis.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']

    # Save the file temporarily
    img_path = os.path.join('temp', file.filename)
    file.save(img_path)
    
    # Preprocess the image
    img_array = preprocess_image(img_path, IMG_SIZE)
    
    # Make prediction using the CNN model
    prediction = cnn_model.predict(img_array)
    predicted_class_idx = np.argmax(prediction, axis=1)[0]  
    predicted_class_name = class_names[predicted_class_idx]  
    confidence_score = float(np.max(prediction))  # Get the confidence score

    # Clean up the temporary image file
    os.remove(img_path)
    
    # Save the prediction to MongoDB
    try:
        collection.insert_one({
            "image_name": file.filename,
            "predicted_class": predicted_class_name,
            "confidence": confidence_score,
            "timestamp": datetime.datetime.now()  # Add timestamp
        })
        db_status = "Prediction saved to database successfully."
    except Exception as e:
        db_status = f"Failed to save prediction to database: {str(e)}"
    
    # Return the prediction and database status as JSON
    return jsonify({
        'predicted_class': predicted_class_name,
        'confidence': confidence_score,
        'db_status': db_status
    })

@app.route('/get_treatment', methods=['POST'])
def get_treatment():
    # Extract data from the form
    predicted_class = request.form.get("predicted_class")
    severity = request.form.get("severity")
    age = request.form.get("age")
    size = request.form.get("size")
    watering_frequency = request.form.get("wateringFrequency")
    location = request.form.get("location")
    variety = request.form.get("variety")
    past_treatments = request.form.get("pastTreatments", "None specified")

    # Generate prompt for the Gemini API
    prompt = f"""
    You are a tomato disease treatment expert. The tomato leaf has been classified with the disease '{predicted_class}'. 
    Additional details: 
    - Severity: {severity}
    - Plant Age: {age}
    - Size: {size}
    - Watering Frequency: {watering_frequency} times per week
    - Location: {location}
    - Variety: {variety}
    - Past Treatments: {past_treatments}
    
    Based on these details, please suggest a personalized treatment plan in HTML format.
    """
    chat_session = genai_model.start_chat(history=[])
    response = chat_session.send_message(prompt)
    clean_response = response.text.replace("```html", "").replace("```", "").strip()
    return jsonify({"response": clean_response})

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form.get("question")
    chat_session1 = genai_model.start_chat(history=[])
    response = chat_session1.send_message(f"You are a tomato leaf disease expert. Please provide a structured and organized answer in HTML format for: {user_input}.")
    clean_response = response.text.replace("```html", "").replace("```", "").strip()
    return jsonify({"response": clean_response})

@app.route('/types')
def types():
    return render_template('types.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/statistics-data', methods=['GET'])
def get_statistics_data():
    try:
        disease_counts = collection.aggregate([
            {"$group": {"_id": "$predicted_class", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        
        # Convert cursor to a list and format the response
        data = [{"disease": doc["_id"], "count": doc["count"]} for doc in disease_counts if doc["_id"]]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure the temp directory exists
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(host='0.0.0.0')
