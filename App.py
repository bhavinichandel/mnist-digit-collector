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

if len(sheet.get_all_values()) == 0:
    sheet.append_row(headers)

# =========================
# UI
# =========================

st.title("MNIST Digit Collector")

# NAME (keep as it is)
name = st.text_input("Enter your name")

# =========================
# LABEL (+ / - ORIGINAL STYLE)
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
# CANVAS (STABLE - ORIGINAL FEEL)
# =========================

canvas = st_canvas(
    fill_color="black",
    stroke_width=15,
    stroke_color="white",
    background_color="black",
    height=280,
    width=280,
    drawing_mode="freedraw",
    key="canvas"
)

# =========================
# HELPERS
# =========================

def is_blank(img):
    return np.mean(img) < 5

# store drawing safely
if canvas.image_data is not None:
    st.session_state.last_draw = canvas.image_data

# =========================
# SAVE BUTTON
# =========================

if st.button("Save to Google Sheets"):

    if not name:
        st.error("Enter your name")
        st.stop()

    if "last_draw" not in st.session_state:
        st.error("Canvas is empty. Draw something first.")
        st.stop()

    img = Image.fromarray(st.session_state.last_draw.astype("uint8"))

    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2GRAY)
    mnist_img = cv2.resize(gray, (28, 28))

    if is_blank(mnist_img):
        st.error("Canvas is empty")
        st.stop()

    pixels = mnist_img.flatten().tolist()

    sheet.append_row([name, digit_label] + pixels)

    st.success("Saved successfully ✅")

    # =========================
    # CLEAR CANVAS AFTER SAVE
    # =========================

    st.session_state.pop("last_draw", None)
    st.rerun()
