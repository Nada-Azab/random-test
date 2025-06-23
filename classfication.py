from flask import Flask, render_template, request, redirect, url_for
from tensorflow.keras.models import load_model
from flask import jsonify

import numpy as np
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Load the trained model
model = load_model('Dense_model.h5')

# Define target image size
IMG_WIDTH = 224
IMG_HEIGHT = 224
CLASS_NAMES = ['F0', 'F1', 'F2', 'F3', 'F4']

def preprocess_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((IMG_WIDTH, IMG_HEIGHT))
    img_array = np.array(img).astype('float32') / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@app.route('/', methods=['GET', 'POST'])

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    img_array = preprocess_image(filepath)
    prediction_probs = model.predict(img_array)[0]
    prediction_index = np.argmax(prediction_probs)
    prediction_label = CLASS_NAMES[prediction_index]

    return jsonify({
        'prediction': prediction_label,
        'confidence': float(prediction_probs[prediction_index])
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
