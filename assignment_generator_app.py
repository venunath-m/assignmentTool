# ---------------------------- assignment_generator_app.py (Updated with dynamic PDF fonts) ----------------------------
import streamlit as st
from duckduckgo_search import duckduckgo_search
import wikipedia
from docx import Document
from docx.shared import Inches
from fpdf import FPDF
from PIL import Image
from io import BytesIO
import requests
import tempfile
import time
from pathlib import Path
from styles import render_header, info_box, floating_icons
from languages import language_code_map
from language_font import language_font_map
from deep_translator import GoogleTranslator
from openai import OpenAI
from dotenv import load_dotenv
import os

# ---------------------------- Paths ----------------------------
FONTS_FOLDER = Path(__file__).parent / "fonts"
ASSETS_FOLDER = Path(__file__).parent / "assets"


# ---------------------------- Load OpenAI API Key ----------------------------
load_dotenv()
# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# ---------------------------- Wikipedia Setup ----------------------------
wikipedia.set_lang("en")
wikipedia.set_rate_limiting(True)

# ---------------------------- Translation Helper ----------------------------
def translate_text(text, target_language_code):
    try:
        if target_language_code == "en":
            return text
        return GoogleTranslator(source='auto', target=target_language_code).translate(text)
    except Exception as e:
        print(f"Translation failed: {e}")
        return text

# ---------------------------- Content Fetching ----------------------------
def fetch_wikipedia_content_with_images(keyword, max_points=10, max_images=3, retries=2):
    suggestions = []
    for _ in range(retries + 1):
        try:
            page = wikipedia.page(keyword)
            content = page.content
            images = [img for img in page.images if img.lower().endswith(('.png', '.jpg', '.jpeg'))][:max_images]

            paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
            intro = paragraphs[0] if paragraphs else "[No intro available]"

            key_points = []
            for para in paragraphs[1:]:
                for s in para.split('. '):
                    s = s.strip()
                    if s and s not in key_points:
                        key_points.append(s)
                    if len(key_points) >= max_points:
                        break
                if len(key_points) >= max_points:
                    break

            return intro, key_points, images, suggestions

        except wikipedia.exceptions.DisambiguationError as e:
            suggestions = e.options[:5]
            try:
                page = wikipedia.page(e.options[0])
                content = page.content
                images = [img for img in page.images if img.lower().endswith(('.png', '.jpg', '.jpeg'))][:max_images]
                paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
                intro = paragraphs[0] if paragraphs else "[No intro available]"

                key_points = []
                for para in paragraphs[1:]:
                    for s in para.split('. '):
                        s = s.strip()
                        if s and s not in key_points:
                            key_points.append(s)
                        if len(key_points) >= max_points:
                            break
                return intro, key_points, images, suggestions
            except:
                continue
        except wikipedia.exceptions.PageError:
            suggestions = wikipedia.search(keyword)[:5]
            return None, [], [], suggestions
        except:
            time.sleep(1)
    return None, [], [], suggestions

def fetch_duckduckgo_content(keyword, max_points=10, retries=2):
    for _ in range(retries + 1):
        try:
            results = duckduckgo_search(keyword, max_results=5)
            if not results:
                continue

            combined_text = ""
            for r in results:
                if 'body' in r and r['body']:
                    combined_text += r['body'] + ". "
                elif 'title' in r and r['title']:
                    combined_text += r['title'] + ". "

            sentences = [s.strip() for s in combined_text.split('. ') if len(s.strip()) > 15]

            key_points = []
            seen = set()
            for s in sentences:
                if s not in seen:
                    key_points.append(s)
                    seen.add(s)
                if len(key_points) >= max_points:
                    break

            intro = key_points[0] if key_points else combined_text[:200] + "..."
            return intro, key_points

        except:
            time.sleep(1)
    return None, []

# ---------------------------- Image Handling ----------------------------
def fetch_and_prepare_image(img_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(img_url, headers=headers, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        if img.mode != "RGB":
            img = img.convert("RGB")
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        img.save(tmp_file.name, format="JPEG")
        tmp_file.close()
        return tmp_file.name
    except Exception as e:
        print(f"Failed to process image {img_url}: {e}")
        return None

# ---------------------------- AI Content Enrichment ----------------------------
def ai_enrich_content(topic, current_text):
    """
    Expand and improve the given content for a topic using OpenAI GPT-4.
    Returns enriched text or error message if enrichment fails.
    """
    prompt = f"Expand and improve the following content for topic '{topic}'. Make it clear and structured for assignment writing:\n\n{current_text}\n\nInclude clear introduction, key points, and examples if possible."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful content writer assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        enriched_text = response.choices[0].message.content.strip()
        return enriched_text
    except Exception as e:
        return f"[AI enrichment failed: {e}]"

# ---------------------------- DOCX & PDF Generation ----------------------------
def generate_docx(content, images_dict, title="Assignment", max_img_per_row=3):
    doc = Document()
    doc.add_heading(title, 0)
    topics = content.split("="*50)

    for topic_section in topics:
        if not topic_section.strip():
            continue

        # Add text content
        doc.add_paragraph(topic_section.strip())
        lines = topic_section.strip().split("\n")
        topic_name = lines[0].replace("=== Topic: ", "").strip() if lines else None

        # Add images in table/grid
        if topic_name and topic_name in images_dict and images_dict[topic_name]:
            imgs = images_dict[topic_name]
            num_rows = (len(imgs) + max_img_per_row - 1) // max_img_per_row
            table = doc.add_table(rows=num_rows, cols=max_img_per_row)
            table.autofit = True

            img_idx = 0
            for r in range(num_rows):
                row_cells = table.rows[r].cells
                for c in range(max_img_per_row):
                    if img_idx >= len(imgs):
                        break
                    tmp_file = fetch_and_prepare_image(imgs[img_idx])
                    if tmp_file:
                        try:
                            paragraph = row_cells[c].paragraphs[0]
                            run = paragraph.add_run()
                            run.add_picture(tmp_file, width=Inches(2.5))  # Adjust size
                        except Exception as e:
                            print(f"Failed to add image {imgs[img_idx]}: {e}")
                    img_idx += 1
            doc.add_paragraph()  # spacing after table

    f = BytesIO()
    doc.save(f)
    f.seek(0)
    return f

def generate_pdf(content, images_dict, title="Assignment", font_path=None, max_img_per_row=3):
    from fpdf import FPDF
    from io import BytesIO

    pdf = FPDF()
    pdf.add_page()

    # Add Unicode font
    font_path = font_path or str(FONTS_FOLDER / "NotoSans-Regular.ttf")
    pdf.add_font("CustomFont", "", font_path)
    pdf.add_font("CustomFont", "B", font_path)

    # Title
    pdf.set_font("CustomFont", 'B', 16)
    pdf.multi_cell(0, 10, title, align="C")
    pdf.ln(10)

    # Content
    pdf.set_font("CustomFont", '', 12)
    pdf.multi_cell(0, 8, content)
    pdf.ln(5)

    # Add Images per topic in grid
    for topic, imgs in images_dict.items():
        if imgs:
            pdf.set_font("CustomFont", 'B', 14)
            pdf.multi_cell(0, 10, f"Images for topic: {topic}")
            pdf.ln(2)

            page_width = pdf.w - 20  # 10pt margin both sides
            img_count = 0
            x_start = 10
            y_start = pdf.get_y()
            row_heights = []

            for img_url in imgs:
                tmp_file = fetch_and_prepare_image(img_url)
                if tmp_file:
                    try:
                        img = Image.open(tmp_file)
                        width, height = img.size
                        # Compute max width per image in row
                        max_width = page_width / max_img_per_row - 5  # 5pt spacing
                        ratio = width / height
                        display_width = min(width, max_width)
                        display_height = display_width / ratio
                        row_heights.append(display_height)

                        # Position
                        x_pos = x_start + (img_count % max_img_per_row) * (page_width / max_img_per_row)
                        y_pos = y_start
                        pdf.image(tmp_file, x=x_pos, y=y_pos, w=display_width, h=display_height)

                        img_count += 1

                        # New row
                        if img_count % max_img_per_row == 0:
                            y_start += max(row_heights) + 5
                            row_heights = []
                            pdf.set_y(y_start)

                    except Exception as e:
                        print(f"Failed to embed image {img_url}: {e}")
                        continue

            # Move cursor below the last row of images
            if row_heights:
                y_start += max(row_heights) + 10
                pdf.set_y(y_start)

    pdf_bytes = pdf.output(dest="S")
    return BytesIO(pdf_bytes)


# ---------------------------- Streamlit UI ----------------------------
st.set_page_config(page_title="Assignment Generator", page_icon=str(ASSETS_FOLDER / "logo.png"), layout="wide")
floating_icons()
render_header(ASSETS_FOLDER, lottie_url="https://assets6.lottiefiles.com/packages/lf20_jcikwtux.json")
info_box()

# ---------------------------- Language Selection ----------------------------
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

selected_language = st.selectbox(
    "Select Language:",
    options=list(language_code_map.keys()),
    index=list(language_code_map.keys()).index(st.session_state.selected_language)
)
st.session_state.selected_language = selected_language
lang_code = language_code_map[selected_language]

# ---------------------------- Mode Selector ----------------------------
mode = st.radio("Select Mode:", ["Student Assignment", "Content Writer"], horizontal=True)

# ---------------------------- Helper to get font ----------------------------
def get_font_path_for_language(lang):
    return FONTS_FOLDER / language_font_map.get(lang, language_font_map["default"])

# ---------------------------- STUDENT ASSIGNMENT UI ----------------------------
if mode == "Student Assignment":
    keywords_input = st.text_area("Enter keywords/topics (comma-separated)", placeholder="e.g., Photosynthesis, Chlorophyll, Light Reactions", value="")
    output_format = st.radio("Select output format:", ["DOCX", "PDF"], key="student_output_format")
    max_points = st.number_input("Maximum key points per topic:", min_value=3, max_value=20, value=10)
    max_images = st.number_input("Maximum images per topic:", min_value=1, max_value=5, value=3)

    generate_clicked = st.button("📝 Generate Assignment", key="generate_btn")
    if generate_clicked and keywords_input.strip():
        keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
        st.info("Fetching content and generating assignment... this may take a few seconds.")

        enriched_content = {}
        images_dict = {}
        for kw in keywords:
            intro, key_points, images, suggestions = fetch_wikipedia_content_with_images(
                kw, max_points=max_points, max_images=max_images
            )
            images_dict[kw] = images
            if not intro:
                ddg_intro, ddg_points = fetch_duckduckgo_content(kw, max_points=max_points)
                intro = ddg_intro if ddg_intro else "[No content available]"
                key_points = ddg_points if ddg_points else ["[No key points available]"]

            intro = translate_text(intro, lang_code)
            key_points = [translate_text(kp, lang_code) for kp in key_points]

            content_text = f"**Introduction:** {intro}\n\n**Key Points:**\n- " + "\n- ".join(key_points)

            tab1, tab2 = st.tabs([f"Original '{kw}'", f"AI Enriched '{kw}'"])
            with tab1:
                st.text_area(f"Content for '{kw}' (Original)", value=content_text, height=200)
            with tab2:
                enriched_text = ai_enrich_content(kw, content_text)
                st.text_area(f"Content for '{kw}' (AI Enriched)", value=enriched_text, height=200)

            enriched_content[kw] = content_text

        # Save for download
        st.session_state.enriched_content = enriched_content
        st.session_state.images_dict = images_dict
        st.session_state.keywords = keywords
        st.session_state.assignment_generated = True
        st.success("Assignment generated successfully!")

# ---------------------------- CONTENT WRITER UI ----------------------------
elif mode == "Content Writer":
    keywords_input = st.text_area(
        "Enter topics for content creation (comma-separated)",
        placeholder="e.g., Photosynthesis, Chlorophyll, Light Reactions",
        value=""
    )
    max_points = st.number_input("Maximum key points per topic:", min_value=3, max_value=20, value=10)
    output_format = st.radio("Select output format for download:", ["DOCX", "PDF"], key="writer_output_format")

    generate_clicked = st.button("🖋️ Generate Content", key="generate_content_btn")
    if generate_clicked and keywords_input.strip():
        keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
        st.info("Fetching content... this may take a few seconds.")

        enriched_content = {}
        images_dict = {}

        for kw in keywords:
            intro, key_points, images, suggestions = fetch_wikipedia_content_with_images(
                kw, max_points=max_points
            )
            images_dict[kw] = images
            if not intro:
                ddg_intro, ddg_points = fetch_duckduckgo_content(kw, max_points=max_points)
                intro = ddg_intro if ddg_intro else "[No content available]"
                key_points = ddg_points if ddg_points else ["[No key points available]"]

            intro = translate_text(intro, lang_code)
            key_points = [translate_text(kp, lang_code) for kp in key_points]

            content_text = f"**Introduction:** {intro}\n\n**Key Points:**\n- " + "\n- ".join(key_points)

            tab1, tab2 = st.tabs([f"Original '{kw}'", f"AI Enriched '{kw}'"])
            with tab1:
                st.text_area(f"Original content for '{kw}'", value=content_text, height=200)
            with tab2:
                enriched_text = ai_enrich_content(kw, content_text)
                st.text_area(f"AI Enriched content for '{kw}'", value=enriched_text, height=200)

            enriched_content[kw] = content_text

        st.session_state.enriched_content = enriched_content
        st.session_state.images_dict = images_dict
        st.session_state.keywords = keywords
        st.session_state.assignment_generated = True
        st.success("Content generated successfully!")

# ---------------------------- DISPLAY IMAGES + DOWNLOAD ----------------------------
if st.session_state.get("assignment_generated", False):
    enriched_content = st.session_state.enriched_content
    images_dict = st.session_state.images_dict
    keywords = st.session_state.keywords

    # Display images
    for topic, imgs in images_dict.items():
        if imgs:
            st.subheader(f"Images for topic: {topic}")
            for idx, img_url in enumerate(imgs):
                st.image(img_url, width=300)
                tmp_file = fetch_and_prepare_image(img_url)
                if tmp_file:
                    with open(tmp_file, "rb") as f:
                        st.download_button(
                            label=f"⬇️ Download Image {idx+1} for {topic}",
                            data=f,
                            file_name=f"{topic.replace(' ', '_')}_{idx+1}.jpg",
                            mime="image/jpeg"
                        )

    # Combine content for download
    combined_content = ""
    for kw in keywords:
        content_text = enriched_content.get(kw, f"Content for {kw} not found.")
        combined_content += f"=== Topic: {kw} ===\n{content_text}\n{'='*50}\n"

    file_name = "Assignment_" + "_".join([kw.replace(" ", "_") for kw in keywords])

    # Get font path for selected language
    font_path = get_font_path_for_language(st.session_state.selected_language)

    if output_format == "PDF":
        st.info(
            "💡 **Important:** To view text in your selected language correctly on your local device, "
            "please ensure the corresponding font is installed if needed. Opening online usually works fine."
        )
        file_data = generate_pdf(combined_content, images_dict, title=file_name, font_path=str(font_path))
        st.download_button(
            "⬇️ Download PDF",
            data=file_data,
            file_name=f"{file_name}.pdf",
            mime="application/pdf"
        )
    else:
        file_data = generate_docx(combined_content, images_dict, title=file_name)
        st.download_button(
            "⬇️ Download DOCX",
            data=file_data,
            file_name=f"{file_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
