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
            "<h1 style='margin:0; padding-top:20px; font-family:Comic Sans MS; color:#4a148c;'>📝 Student Assignment Generator</h1>",
            unsafe_allow_html=True
        )
    with col3:
        if lottie_anim:
            st_lottie(lottie_anim, speed=1, width=120, height=120, key="student_anim")

# ---------------------------- Info Box ----------------------------
def info_box():
    st.markdown("""
    <div style='background: linear-gradient(90deg, #E0F7FA 0%, #B2EBF2 100%);
                padding:20px; border-radius:15px; margin-top:15px; box-shadow: 0 5px 15px rgba(0,0,0,0.2);'>
        <h3 style='color:#00796B; margin-bottom:5px;'>🎯 How to Use</h3>
        <p style='color:#004D40; font-size:15px;'>
            Enter your topic keywords separated by commas.<br>
            Select output format (DOCX or PDF).<br>
            Click 'Generate Assignment' to create a structured assignment with images.<br>
            Have fun while learning! 🚀
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------- Floating Motivational Icons ----------------------------
def floating_icons():
    st.markdown("""
    <style>
    @keyframes floatUp {
        0% { transform: translateY(0); opacity:1; }
        50% { transform: translateY(-20px); opacity:0.8; }
        100% { transform: translateY(0); opacity:1; }
    }
    .floating-icon {
        position: fixed;
        width: 50px;
        animation: floatUp 5s ease-in-out infinite;
    }
    </style>

    <img src='https://img.icons8.com/color/48/000000/rocket.png' class='floating-icon' style='top:10%; left:5%; animation-delay:0s;'>
    <img src='https://img.icons8.com/color/48/000000/light-on.png' class='floating-icon' style='top:60%; left:90%; animation-delay:2s;'>
    <img src='https://img.icons8.com/color/48/000000/laptop.png' class='floating-icon' style='top:40%; left:50%; animation-delay:4s;'>
    """, unsafe_allow_html=True)

# ---------------------------- Fun HTML Buttons ----------------------------
def html_button(label, key, color="#4CAF50", emoji="🎯"):
    button_html = f"""
    <style>
    .btn-{key} {{
        background: linear-gradient(45deg, #ff6ec4, #7873f5, #42e695);
        background-size: 300% 300%;
        border: none;
        color: white;
        padding: 12px 28px;
        font-size: 16px;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    .btn-{key}:hover {{
        transform: scale(1.1);
        background-position: 100% 0%;
    }}
    </style>
    <form action="javascript:void(0)">
        <button class="btn-{key}" type="submit">{emoji} {label}</button>
    </form>
    """
    st.markdown(button_html, unsafe_allow_html=True)
