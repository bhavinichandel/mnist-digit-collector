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

# ✅ WORKS ON CLOUD + LOCAL (using secrets)
creds = Credentials.from_service_account_info(
    st.secrets["google"],
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open("MNIST Dataset").sheet1

# =========================
# Create headers (ONLY ONCE)
# =========================

headers = ["label"] + [f"pixel_{i}" for i in range(784)]

data = sheet.get_all_values()

if len(data) == 0:
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
# Convert image
# =========================

def is_blank(img):
    return np.mean(img) < 5  # prevent empty save

if canvas_result.image_data is not None:

    img = Image.fromarray(canvas_result.image_data.astype("uint8"))
    st.image(img, caption="Original")

    img_array = np.array(img)

    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
    mnist_img = cv2.resize(gray, (28, 28))

    st.image(mnist_img, caption="28x28 MNIST Image", width=200)

    st.write("Shape:", mnist_img.shape)

    # =========================
    # SAVE BUTTON
    # =========================

    if st.button("Save to Google Sheets"):

        if is_blank(mnist_img):
            st.error("Canvas is empty! Draw a digit first.")
            st.stop()

        pixels = mnist_img.flatten().tolist()
        row = [int(digit_label)] + pixels

        sheet.append_row(row)

        st.success("Saved to Google Sheets ✅")
