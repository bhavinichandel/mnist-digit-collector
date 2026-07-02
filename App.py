import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image
import cv2
import gspread
from google.oauth2.service_account import Credentials

# =========================
# GOOGLE SHEETS SETUP
# =========================

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["google"],
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open("MNIST Dataset").sheet1

# =========================
# HEADER (SAFE)
# =========================

headers = ["name", "label"] + [f"pixel_{i}" for i in range(784)]
data = sheet.get_all_values()

if len(data) == 0:
    sheet.append_row(headers)

# =========================
# UI
# =========================

st.title("MNIST Digit Collector")

name = st.text_input("Enter your name")

# =========================
# LABEL CONTROL (+ / -)
# =========================

if "label" not in st.session_state:
    st.session_state.label = 0

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("➖"):
        st.session_state.label = max(0, st.session_state.label - 1)

with col3:
    if st.button("➕"):
        st.session_state.label = min(9, st.session_state.label + 1)

with col2:
    st.markdown(
        f"<h2 style='text-align:center'>Label: {st.session_state.label}</h2>",
        unsafe_allow_html=True
    )

digit_label = st.session_state.label

# =========================
# CANVAS RESET CONTROL (IMPORTANT FIX)
# =========================

if "canvas_id" not in st.session_state:
    st.session_state.canvas_id = 0

def reset_canvas():
    st.session_state.canvas_id += 1

# =========================
# CANVAS
# =========================

canvas = st_canvas(
    fill_color="black",
    stroke_width=15,
    stroke_color="white",
    background_color="black",
    height=280,
    width=280,
    drawing_mode="freedraw",
    key=f"canvas_{st.session_state.canvas_id}",
)

# =========================
# HELPERS
# =========================

def is_blank(img):
    return np.mean(img) < 5

# =========================
# PROCESS IMAGE
# =========================

if canvas.image_data is not None:

    img = Image.fromarray(canvas.image_data.astype("uint8"))

    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2GRAY)
    mnist_img = cv2.resize(gray, (28, 28))

    st.image(mnist_img, caption="28x28 MNIST")

    # =========================
    # SAVE BUTTON
    # =========================

    if st.button("Save to Google Sheets"):

        if not name:
            st.error("Enter your name")
            st.stop()

        if is_blank(mnist_img):
            st.error("Canvas is empty")
            st.stop()

        pixels = mnist_img.flatten().tolist()

        sheet.append_row([name, digit_label] + pixels)

        st.success("Saved successfully ✅")

        # 🔥 THIS IS THE FIX (CLEAR CANVAS)
        reset_canvas()
        st.rerun()
