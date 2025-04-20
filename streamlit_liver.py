import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Force TensorFlow to run on CPU

import streamlit as st
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array

# ==========================
# CONFIGURATION
# ==========================
IMG_SIZE = (224, 224)
CLASS_ORDER = ['F0', 'F1', 'F2', 'F3', 'F4']

# ==========================
# CUSTOM CSS
# ==========================
def inject_custom_css():
    st.markdown("""
    <style>
        :root {
            --primary: #2c3e50;
            --secondary: #3498db;
            --accent: #e74c3c;
        }
        
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            font-family: 'Arial', sans-serif;
        }
        
        .header {
            background-color: var(--primary);
            color: white;
            padding: 1rem 2rem;
            border-radius: 0 0 10px 10px;
            margin-bottom: 2rem;
        }
        
        .nav {
            display: flex;
            gap: 2rem;
            margin-bottom: 1rem;
        }
        
        .nav a {
            color: white;
            text-decoration: none;
            font-weight: bold;
        }
        
        .organ-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .normal {
            color: #27ae60;
        }
        
        .abnormal {
            color: #e74c3c;
        }
        
        .calendar {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 5px;
            margin-top: 1rem;
        }
        
        .calendar-day {
            padding: 8px;
            text-align: center;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .doctor-card {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================
# LOAD MODEL
# ==========================
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("/content/Dense_model.path/kaggle/working/Dense_model_.h5")

# ==========================
# PREPROCESS IMAGE
# ==========================
def preprocess_image(image: Image.Image) -> np.ndarray:
    image = image.resize(IMG_SIZE)
    image_array = img_to_array(image) / 255.0  # Normalize to [0,1]
    return np.expand_dims(image_array, axis=0)

# ==========================
# PREDICT FIBROSIS
# ==========================
def predict_fibrosis(model, img_tensor, class_labels):
    prediction = model.predict(img_tensor)
    predicted_class = np.argmax(prediction)
    predicted_label = class_labels[predicted_class]
    fibrosis_status = "No Fibrosis" if predicted_label == "F0" else "Fibrosis Detected"
    return fibrosis_status, predicted_label, prediction

# ==========================
# WEBSITE LAYOUT
# ==========================
def main():
    inject_custom_css()
    
    # Header with Navigation
    st.markdown("""
    <div class="header">
        <h1>GASTROCHECK</h1>
        <div class="nav">
            <a href="#home">Home</a>
            <a href="#therapy">Therapy</a>
            <a href="#centers">Our Centers</a>
            <a href="#specialists">Specialists</a>
            <a href="#contact">Contact</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Two-column layout
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # Organ Status Section
        st.markdown("## Organ Status")
        
        organs = [
            ("Liver", "Normal", "normal"),
            ("Large Intestine (Colon)", "Normal", "normal"),
            ("Gallbladder", "Biliary Dysfunction", "abnormal"),
            ("Stomach", "Endure Chaffitis", "abnormal"),
            ("Small Intestine", "No Antisexual Fencing", "normal"),
            ("Pancreas", "Normal Function", "normal"),
            ("Esophagus", "Mid Endopaths", "abnormal"),
            ("Duodenum", "No inflammation", "normal")
        ]
        
        for organ, status, status_class in organs:
            st.markdown(f"""
            <div class="organ-card">
                <h3>{organ}</h3>
                <p class="{status_class}">{status}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Main Content - Fibrosis Classifier
        st.markdown("## Liver Fibrosis Classification")
        st.write("Upload a liver ultrasound image to classify the fibrosis stage.")
        
        uploaded_file = st.file_uploader("📤 Upload an image...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption='🖼️ Uploaded Image', use_column_width=True)
            
            model = load_model()
            img_tensor = preprocess_image(image)
            fibrosis_status, predicted_stage, preds = predict_fibrosis(model, img_tensor, CLASS_ORDER)
            confidence = float(np.max(preds)) * 100
            
            stage_color = {
                "F0": "🟢",
                "F1": "🟡",
                "F2": "🟠",
                "F3": "🟠",
                "F4": "🔴"
            }
            
            st.markdown(f"""
            <div class="organ-card">
                <h3>Liver Fibrosis Analysis</h3>
                <p><strong>Stage:</strong> {stage_color[predicted_stage]} {predicted_stage}</p>
                <p><strong>Status:</strong> {fibrosis_status}</p>
                <p><strong>Confidence:</strong> {confidence:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Treatment Section
        st.markdown("## Treatment")
        st.markdown("""
        <div class="organ-card">
            <h3>Dr. Sam Bennett</h3>
            <p>To manage kidney dysfunction and preweigastritis, dietary adjustments including a low-fat regimen are recommended. Protein Pump inhibitors (PPIs) may be prescribed to reduce treatment and support healing. For mild eosinolysis, antacids or suppression medications can be used. Stress reduction techniques and regular physical activity are advised to promote overall digestive health.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Appointment Section
        st.markdown("## Book an Appointment")
        st.selectbox("Specialization:", ["Gastroenterologist", "Nutritionist", "General Practitioner"])
        
        st.markdown("### November 2024")
        st.markdown("""
        <div class="calendar">
            <div class="calendar-day">M</div>
            <div class="calendar-day">T</div>
            <div class="calendar-day">W</div>
            <div class="calendar-day">T</div>
            <div class="calendar-day">F</div>
            <div class="calendar-day">S</div>
            <div class="calendar-day">S</div>
            
            <div class="calendar-day">28</div>
            <div class="calendar-day">29</div>
            <div class="calendar-day">30</div>
            <div class="calendar-day">31</div>
            <div class="calendar-day">1</div>
            <div class="calendar-day">2</div>
            <div class="calendar-day">3</div>
            
            <!-- Continue with other days -->
        </div>
        """, unsafe_allow_html=True)
        
        # Doctors Section
        st.markdown("## Doctors")
        doctors = [
            ("Dr. Alan Thompson", "Gastroenterology"),
            ("Dr. Michael Roberts", "Gastroenterologist"),
            ("Dr. Sarah Bennett", "Doctoral practitioner"),
            ("Dr. Emily Carter", "Nutritionist"),
            ("Dr. James Parker", "Doctoral practitioner"),
            ("Dr. Christopher Davis", "Business")
        ]
        
        for name, specialty in doctors:
            st.markdown(f"""
            <div class="doctor-card">
                <div>
                    <h4>{name}</h4>
                    <p>{specialty}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(page_title="GASTROCHECK", layout="wide")
    main()
