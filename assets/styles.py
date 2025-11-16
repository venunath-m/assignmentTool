# styles.py
import streamlit as st
import requests
from streamlit_lottie import st_lottie

# ---------------------------- Lottie Animations ----------------------------
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# ---------------------------- Header Section ----------------------------
def render_header(assets_path, lottie_url=None):
    lottie_anim = load_lottieurl(lottie_url) if lottie_url else None
    col1, col2, col3 = st.columns([1, 6, 2])
    with col1:
        st.image(str(assets_path / "logo.png"), width=80)
    with col2:
        st.markdown(
            "<h1 style='margin:0; padding-top:20px; font-family:Comic Sans MS;'>📝 Student Assignment Generator</h1>",
            unsafe_allow_html=True
        )
    with col3:
        if lottie_anim:
            st_lottie(lottie_anim, speed=1, width=120, height=120, key="student_anim")

# ---------------------------- Info Box ----------------------------
def info_box():
    st.markdown(
        """
        <div style='background: linear-gradient(90deg, #E0F7FA 0%, #B2EBF2 100%);
                    padding:15px; border-radius:10px; margin-top:10px;'>
            <h3 style='color:#00796B; margin-bottom:5px;'>🎯 How to Use</h3>
            <p style='color:#004D40; font-size:15px;'>
                Enter your topic keywords separated by commas.<br>
                Select output format (DOCX or PDF).<br>
                Click 'Generate Assignment' to create a structured assignment with images.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------- Fun HTML Buttons ----------------------------
def html_button(label, key, color="#4CAF50", emoji="🎯"):
    button_html = f"""
    <style>
    .btn-{key} {{
        background-color: {color};
        border: none;
        color: white;
        padding: 12px 28px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 5px 2px;
        cursor: pointer;
        border-radius: 12px;
        transition: all 0.3s ease;
    }}
    .btn-{key}:hover {{
        background-color: #45a049;
        transform: scale(1.05);
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }}
    </style>
    <form action="javascript:void(0)">
        <button class="btn-{key}" type="submit">{emoji} {label}</button>
    </form>
    """
    st.markdown(button_html, unsafe_allow_html=True)
