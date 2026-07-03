import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image
import cv2
import gspread
from google.oauth2.service_account import Credentials

# =========================
# Google Sheets Setup
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
# Create headers (ONLY ONCE)
# =========================

headers = ["name", "label"] + [f"pixel_{i}" for i in range(784)]
data = sheet.get_all_values()

if len(data) == 0:
    sheet.append_row(headers)

# =========================
# Streamlit UI
# =========================

st.title("MNIST Digit Collector")

# =========================
# Session State
# =========================

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

if "digit_label" not in st.session_state:
    st.session_state.digit_label = "0"

# =========================
# NAME
# =========================

name = st.text_input("Enter your name")

# =========================
# LABEL (TEXT INPUT)
# =========================

digit_label = st.text_input(
    "Digit Label (0-9)",
    value=st.session_state.digit_label,
    key="label_input"
)

# =========================
# CANVAS
# =========================

canvas_result = st_canvas(
    fill_color="black",
    stroke_width=15,
    stroke_color="white",
    background_color="black",
    height=280,
    width=280,
    drawing_mode="freedraw",
    key=f"canvas_{st.session_state.canvas_key}",
)

# =========================
# Image Functions
# =========================

def is_blank(img):
    return np.mean(img) < 5

# =========================
# Process Image
# =========================

if canvas_result.image_data is not None:

    img = Image.fromarray(canvas_result.image_data.astype("uint8"))
    st.image(img, caption="Original")

    img_array = np.array(img)

    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)

    mnist_img = cv2.resize(gray, (28, 28))

    st.image(mnist_img, caption="28x28 MNIST Image", width=200)

    # =========================
    # SAVE BUTTON
    # =========================

    if st.button("Save to Google Sheets"):

        # Name Validation
        if not name.strip():
            st.error("Please enter your name.")
            st.stop()

        # Label Validation
        if len(digit_label) != 1 or not digit_label.isdigit():
            st.error("Please enter exactly one digit between 0 and 9.")
            st.stop()

        if digit_label not in [str(i) for i in range(10)]:
            st.error("Digit label must be between 0 and 9.")
            st.stop()

        # Blank Canvas Validation
        if is_blank(mnist_img):
            st.error("Canvas is empty! Draw a digit first.")
            st.stop()

        # Pixels
        pixels = mnist_img.flatten().tolist()

        row = [name, int(digit_label)] + pixels

        sheet.append_row(row)

        st.success("Saved to Google Sheets ✅")

        # =========================
        # Auto Increase Label
        # =========================

        next_digit = (int(digit_label) + 1) % 10
        st.session_state.digit_label = str(next_digit)

        # =========================
        # Clear Canvas
        # =========================

        st.session_state.canvas_key += 1

        st.rerun()
