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

creds = Credentials.from_service_account_file(
    "mnist-digit-collector-501215-027e3c59a746.json",
    scopes=scopes
)

client = gspread.authorize(creds)

sheet = client.open("MNIST Dataset").sheet1

# =========================
# Create headers (ONLY ONCE)
# =========================

headers = ["label"] + [f"pixel_{i}" for i in range(784)]

if sheet.cell(1, 1).value is None:
    sheet.append_row(headers)

# =========================
# Streamlit UI
# =========================

st.title("MNIST Digit Collector")

digit_label = st.number_input(
    "Digit Label (0-9)",
    min_value=0,
    max_value=9,
    step=1
)

# =========================
# Canvas
# =========================

canvas_result = st_canvas(
    fill_color="black",
    stroke_width=15,
    stroke_color="white",
    background_color="black",
    height=280,
    width=280,
    drawing_mode="freedraw",
    key="canvas",
)

# =========================
# Image Processing
# =========================

if canvas_result.image_data is not None:

    img = Image.fromarray(canvas_result.image_data.astype("uint8"))
    st.image(img, caption="Original Image (280x280)")

    img_array = np.array(img)

    # Convert RGBA → grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
    st.image(gray, caption="Grayscale Image")

    # Resize to MNIST format
    mnist_img = cv2.resize(gray, (28, 28))
    st.image(mnist_img, caption="MNIST Image (28x28)", width=200)

    st.write("Shape:", mnist_img.shape)

    # =========================
    # SAVE TO GOOGLE SHEETS
    # =========================

    if st.button("Save to Google Sheets"):

        pixels = mnist_img.flatten().tolist()
        row = [int(digit_label)] + pixels

        sheet.append_row(row)

        st.success("Saved to Google Sheets ✅")