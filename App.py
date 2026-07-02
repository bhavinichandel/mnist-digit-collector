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
# HEADER SETUP
# =========================

headers = ["name", "label"] + [f"pixel_{i}" for i in range(784)]
data = sheet.get_all_values()

if len(data) == 0:
    sheet.append_row(headers)

# =========================
# UI
# =========================

st.title("MNIST Digit Collector")

name = st.text_input("Enter your name", key="name")

# -------------------------
# LABEL (SESSION STATE FIX)
# -------------------------

if "label" not in st.session_state:
    st.session_state.label = 0

digit_label = st.number_input(
    "Digit Label (0-9)",
    min_value=0,
    max_value=9,
    step=1,
    key="label"
)

# =========================
# CANVAS STATE CONTROL
# =========================

if "canvas_reset" not in st.session_state:
    st.session_state.canvas_reset = False

canvas_key = "canvas_" + str(st.session_state.canvas_reset)

canvas_result = st_canvas(
    fill_color="black",
    stroke_width=15,
    stroke_color="white",
    background_color="black",
    height=280,
    width=280,
    drawing_mode="freedraw",
    key=canvas_key,
)

# =========================
# HELPERS
# =========================

def is_blank(img):
    return np.mean(img) < 5

def reset_inputs():
    # reset canvas
    st.session_state.canvas_reset = not st.session_state.canvas_reset

    # reset label
    st.session_state.label = 0

# =========================
# PROCESS IMAGE
# =========================

if canvas_result.image_data is not None:

    img = Image.fromarray(canvas_result.image_data.astype("uint8"))

    img_array = np.array(img)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
    mnist_img = cv2.resize(gray, (28, 28))

    st.image(mnist_img, caption="28x28 MNIST Image", width=200)

    # =========================
    # SAVE BUTTON
    # =========================

    if st.button("Save to Google Sheets"):

        if not name:
            st.error("Please enter your name first")
            st.stop()

        if is_blank(mnist_img):
            st.error("Canvas is empty!")
            st.stop()

        pixels = mnist_img.flatten().tolist()

        row = [name, int(digit_label)] + pixels
        sheet.append_row(row)

        st.success("Saved successfully ✅")

        # RESET EVERYTHING
        reset_inputs()
        st.rerun()
