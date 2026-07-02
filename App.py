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
# SAFE HEADER INIT
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
# STRICT LABEL INPUT (IMPORTANT FIX)
# =========================

label_text = st.text_input("Digit Label (0-9)")

digit_label = None

if label_text != "":

    if not label_text.isdigit():
        st.error("Only numbers allowed (0–9)")
        st.stop()

    if len(label_text) != 1:
        st.error("Only SINGLE digit allowed (0–9). No 11, 00, 777")
        st.stop()

    digit_label = int(label_text)

# =========================
# CANVAS RESET CONTROL
# =========================

if "canvas_id" not in st.session_state:
    st.session_state.canvas_id = 0

def reset_canvas():
    st.session_state.canvas_id = 1 - st.session_state.canvas_id

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
    key=f"canvas_{st.session_state.canvas_id}"
)

# =========================
# IMAGE CHECK
# =========================

def is_blank(img):
    return np.mean(img) < 5

# =========================
# PROCESS IMAGE
# =========================

if canvas.image_data is not None:

    img = Image.fromarray(canvas.image_data.astype("uint8"))

    img_array = np.array(img)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
    mnist_img = cv2.resize(gray, (28, 28))

    st.subheader("Preview")

    col1, col2 = st.columns(2)

    with col1:
        st.image(img, caption="Canvas (280×280)")

    with col2:
        st.image(mnist_img, caption="MNIST (28×28)")

    # =========================
    # SAVE BUTTON
    # =========================

    if st.button("Save to Google Sheets"):

        if not name:
            st.error("Please enter your name")
            st.stop()

        if digit_label is None:
            st.error("Please enter valid digit (0–9)")
            st.stop()

        if is_blank(mnist_img):
            st.error("Canvas is empty!")
            st.stop()

        pixels = mnist_img.flatten().tolist()

        row = [name, digit_label] + pixels

        sheet.append_row(row)

        st.success("Saved successfully ✅")

        reset_canvas()
        st.rerun()
