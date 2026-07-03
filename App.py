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
# Session State
# =========================

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

# Label session state
if "label_input" not in st.session_state:
    st.session_state.label_input = "0"

# =========================
# Streamlit UI
# =========================

st.title("MNIST Digit Collector")

# NAME
name = st.text_input("Enter your name")

# LABEL
digit_label = st.text_input(
    "Digit Label (0-9)",
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
# Helper Function
# =========================

def is_blank(img):
    return np.mean(img) < 5

# =========================
# Convert image
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

        # Name validation
        if not name.strip():
            st.error("Please enter your name.")
            st.stop()

        # Label validation
        if not digit_label.isdigit() or len(digit_label) != 1:
            st.error("Please enter only one digit between 0 and 9.")
            st.stop()

        label = int(digit_label)

        if label < 0 or label > 9:
            st.error("Digit must be between 0 and 9.")
            st.stop()

        # Blank canvas validation
        if is_blank(mnist_img):
            st.error("Canvas is empty! Draw a digit first.")
            st.stop()

        pixels = mnist_img.flatten().tolist()

        row = [name, label] + pixels

        sheet.append_row(row)

        st.success("Saved to Google Sheets ✅")

        # =========================
        # AUTO LABEL
        # =========================

        next_digit = (label + 1) % 10
        st.session_state["label_input"] = str(next_digit)

        # =========================
        # RESET CANVAS
        # =========================

        st.session_state.canvas_key += 1

        st.rerun()
