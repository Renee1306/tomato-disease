from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
from dotenv import load_dotenv
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Load the pre-trained CNN model for image classification
cnn_model = load_model('cnn_model.h5')  # Replace with the actual path to your CNN model

# Define the image size for the CNN model
IMG_SIZE = (256, 256)  # Adjust according to your model input size

# Define the class names (use the ones from your dataset)
class_names = [
    'Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight',
    'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot',
    'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato__Target_Spot',
    'Tomato__Tomato_YellowLeaf__Curl_Virus', 'Tomato__Tomato_mosaic_virus',
    'Tomato_healthy'
]

# Helper function to preprocess image
def preprocess_image(img_path, img_size):
    img = image.load_img(img_path, target_size=img_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array  

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the Generative AI model
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

# Define route for uploading and predicting image
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

    # Clean up the temporary image file
    os.remove(img_path)
    
    # Return the prediction as JSON
    return jsonify({
        'predicted_class': predicted_class_name,
        'confidence': float(np.max(prediction)) 
    })

@app.route('/types')
def types():
    return render_template('types.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form.get("question")
    chat_session = genai_model.start_chat(history=[])
    response = chat_session.send_message(f"You are a tomato leaf disease expert. Please provide a structured and organized answer in HTML format for: {user_input}.")
    clean_response = response.text.replace("```html", "").replace("```", "").strip()
    return jsonify({"response": clean_response})

if __name__ == '__main__':
    # Ensure the temp directory exists
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(debug=True)