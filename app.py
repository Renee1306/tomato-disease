from flask import Flask, request, redirect, url_for, render_template,  jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
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

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No file part", 400
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400
    
    return "File uploaded successfully", 200

@app.route('/types')
def types():
    return render_template('types.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form.get("question")
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(f"Please provide a structured and organized answer in HTML format for: {user_input}.")
    clean_response = response.text.replace("```html", "").replace("```", "").strip()
    return jsonify({"response": clean_response})

if __name__ == '__main__':
    app.run(debug=True)
