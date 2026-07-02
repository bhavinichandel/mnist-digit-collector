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

headers = ["name", "label"] + [f"pixel_{i}" for i in range(784)]

if len(sheet.get_all_values()) == 0:
    sheet.append_row(headers)

# =========================
# UI
# =========================

st.title("MNIST Digit Collector")

name = st.text_input("Enter your name")

label_text = st.text_input("Digit Label (0-9)")

# =========================
# CANVAS
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
# HELPERS
# =========================

def is_blank(img):
    return np.mean(img) < 5

def validate_label(label_str):
    # STRICT RULES HERE (THIS IS KEY FIX)
    if label_str is None:
        return None

    label_str = label_str.strip()

    if label_str == "":
        return None

    if not label_str.isdigit():
        return None

    if len(label_str) != 1:
        return None

    return int(label_str)

def reset_canvas():
    st.session_state.canvas_id = 1 - st.session_state.canvas_id

# =========================
# PROCESS IMAGE
# =========================

if canvas.image_data is not None:

    img = Image.fromarray(canvas.image_data.astype("uint8"))
    img_array = np.array(img)

    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
    mnist_img = cv2.resize(gray, (28, 28))

    st.image(mnist_img, caption="28×28 MNIST")

    # =========================
    # SAVE BUTTON (CRITICAL FIX HERE)
    # =========================

    if st.button("Save to Google Sheets"):

        digit_label = validate_label(label_text)

        # 🔥 VALIDATION DONE AT CLICK TIME (FIXES YOUR 11 ISSUE)
        if digit_label is None:
            st.error("Invalid label! Enter ONLY a single digit (0–9)")
            st.stop()

        if not name:
            st.error("Enter name first")
            st.stop()

        if is_blank(mnist_img):
            st.error("Canvas is empty")
            st.stop()

        pixels = mnist_img.flatten().tolist()

        sheet.append_row([name, digit_label] + pixels)

        st.success("Saved successfully ✅")

        reset_canvas()
        st.rerun()
