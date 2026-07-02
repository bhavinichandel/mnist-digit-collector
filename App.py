import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image
import cv2
import gspread
from google.oauth2.service_account import Credentials

# =========================
# GOOGLE SHEETS
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
# HEADER
# =========================

if len(sheet.get_all_values()) == 0:
    sheet.append_row(["name", "label"] + [f"pixel_{i}" for i in range(784)])

# =========================
# UI
# =========================

st.title("MNIST Digit Collector")

name = st.text_input("Enter your name")
label_text = st.text_input("Digit (0-9)")

# =========================
# CANVAS (STABLE)
# =========================

if "canvas_id" not in st.session_state:
    st.session_state.canvas_id = 0

canvas = st_canvas(
    fill_color="black",
    stroke_width=15,
    stroke_color="white",
    background_color="black",
    height=280,
    width=280,
    drawing_mode="freedraw",
    key=f"canvas_{st.session_state.canvas_id}"
)

# =========================
# SAVE IMAGE INTO MEMORY (IMPORTANT FIX)
# =========================

if canvas.image_data is not None:
    st.session_state.last_image = canvas.image_data

# =========================
# HELPERS
# =========================

def validate_label(x):
    if x is None:
        return None
    x = x.strip()
    if x.isdigit() and len(x) == 1:
        return int(x)
    return None

def reset_canvas():
    st.session_state.canvas_id = 1 - st.session_state.canvas_id

# =========================
# SAVE BUTTON
# =========================

if st.button("Save to Google Sheets"):

    digit_label = validate_label(label_text)

    if digit_label is None:
        st.error("Enter ONLY single digit (0-9)")
        st.stop()

    if not name:
        st.error("Enter name")
        st.stop()

    # 🔥 USE STORED IMAGE (NOT LIVE CANVAS)
    if "last_image" not in st.session_state:
        st.error("Canvas is empty. Draw something first.")
        st.stop()

    img = Image.fromarray(st.session_state.last_image.astype("uint8"))

    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2GRAY)
    mnist_img = cv2.resize(gray, (28, 28))

    if np.mean(mnist_img) < 5:
        st.error("Canvas is empty")
        st.stop()

    pixels = mnist_img.flatten().tolist()

    sheet.append_row([name, digit_label] + pixels)

    st.success("Saved successfully ✅")

    reset_canvas()

    # clear stored image
    del st.session_state["last_image"]

    st.rerun()
