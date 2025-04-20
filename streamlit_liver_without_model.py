import streamlit as st
from PIL import Image
import numpy as np

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="GASTROCHECK",
    page_icon="🏥",
    layout="wide"
)

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
        
        /* Navigation Bar Styles */
        .nav-container {
            background-color: var(--primary);
            padding: 15px 25px;
            border-radius: 0 0 10px 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .nav-logo {
            font-size: 24px;
            font-weight: bold;
            color: white !important;
            margin-right: 40px;
        }
        
        .nav-items {
            display: flex;
            gap: 30px;
        }
        
        .nav-item {
            color: white !important;
            font-size: 16px;
            text-decoration: none;
            font-weight: 500;
        }
        
        .nav-item:hover {
            color: var(--secondary) !important;
        }
        
        .patient-info {
            color: white;
            font-size: 14px;
            margin-left: auto;
        }
        
        /* Rest of your existing styles */
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            font-family: 'Arial', sans-serif;
        }
        
        .organ-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .normal { color: #27ae60; }
        .abnormal { color: #e74c3c; }
        
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
# DEMO DATA
# ==========================
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

doctors = [
    ("Dr. Alan Thompson", "Gastroenterology"),
    ("Dr. Michael Roberts", "Gastroenterologist"),
    ("Dr. Sarah Bennett", "Doctoral practitioner"),
    ("Dr. Emily Carter", "Nutritionist"),
    ("Dr. James Parker", "Doctoral practitioner")
]

# ==========================
# STREAMLIT UI
# ==========================
def main():
    inject_custom_css()
    
    # Navigation Bar (matches your image exactly)
    st.markdown("""
    <div class="nav-container">
        <div class="nav-logo">GASTROCHECK</div>
        <div class="nav-items">
            <a href="#home" class="nav-item">Home</a>
            <a href="#therapy" class="nav-item">Therapy</a>
            <a href="#centers" class="nav-item">Our Centers</a>
            <a href="#specialists" class="nav-item">Specialists</a>
            <a href="#contact" class="nav-item">Contact</a>
        </div>
        <div class="patient-info">
            Michael Harris<br>24 pts
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Two columns layout
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("## Organ Status")
        for organ, status, status_class in organs:
            st.markdown(f"""
            <div class="organ-card">
                <h3>{organ}</h3>
                <p class="{status_class}">{status}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("## Liver Fibrosis Classification")
        uploaded_file = st.file_uploader("Upload liver ultrasound image", type=["jpg", "png", "jpeg"])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Demo results (replace with your model later)
            st.markdown("""
            <div class="organ-card">
                <h3>Liver Fibrosis Analysis</h3>
                <p><strong>Stage:</strong> F2</p>
                <p><strong>Status:</strong> Fibrosis Detected</p>
                <p><strong>Confidence:</strong> 87.3%</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("## Treatment")
        st.markdown("""
        <div class="organ-card">
            <h3>Dr. Sam Bennett</h3>
            <p>To manage kidney dysfunction and preweigastritis, dietary adjustments including a low-fat regimen are recommended. Protein Pump inhibitors (PPIs) may be prescribed to reduce treatment and support healing.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## Book an Appointment")
        st.selectbox("Specialization:", ["Gastroenterologist", "Nutritionist", "General Practitioner"])
        
        st.markdown("### November 2024")
        st.markdown("""
        <div class="calendar">
            <div class="calendar-day">M</div><div class="calendar-day">T</div><div class="calendar-day">W</div>
            <div class="calendar-day">T</div><div class="calendar-day">F</div><div class="calendar-day">S</div>
            <div class="calendar-day">S</div>
            
            <div class="calendar-day">28</div><div class="calendar-day">29</div><div class="calendar-day">30</div>
            <div class="calendar-day">31</div><div class="calendar-day">1</div><div class="calendar-day">2</div>
            <div class="calendar-day">3</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## Doctors")
        for name, specialty in doctors:
            st.markdown(f"""
            <div class="doctor-card">
                <div style="width:50px; height:50px; border-radius:50%; background:#ddd;"></div>
                <div>
                    <h4 style="margin:0;">{name}</h4>
                    <p style="margin:0; color:#666;">{specialty}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
