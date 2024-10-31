from flask import Flask, render_template, request, jsonify
from huggingface_hub import InferenceClient

app = Flask(__name__)
client = InferenceClient(api_key="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")

@app.route('/')
def index():
    return render_template('llama.html')

@app.route('/generate_story', methods=['POST'])
def generate_story():
    user_input = request.json.get('user_input')
    
    messages = [{"role": "user", "content": user_input}]
    
    # Initiating the story generation
    stream = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct",
        messages=messages,
        temperature=0.5,
        max_tokens=1024,
        top_p=0.7,
        stream=True
    )
    
    # Collecting all chunks of generated content
    story_content = ""
    for chunk in stream:
        story_content += chunk.choices[0].delta.content
    
    return jsonify({"story": story_content})

if __name__ == '__main__':
    app.run(debug=True)
