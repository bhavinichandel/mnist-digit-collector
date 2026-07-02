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
# SAFE HEADER CREATION
# =========================

headers = ["name", "label"] + [f"pixel_{i}" for i in range(784)]

data = sheet.get_all_values()

# If sheet is empty OR corrupted → fix headers
if len(data) == 0:
    sheet.append_row(headers)

elif len(data[0]) != 784 + 2:
    sheet.clear()
    sheet.append_row(headers)

# =========================
# UI
# =========================

st.title("MNIST Digit Collector")

name = st.text_input("Enter your name")

digit_label = st.number_input(
    "Digit Label (0-9)",
    min_value=0,
    max_value=9,
    step=1
)

# =========================
# CANVAS STATE (STABLE)
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
    key=f"canvas_{st.session_state.canvas_id}",
)

# =========================
# HELPERS
# =========================

def is_blank(img):
    return np.mean(img) < 5

def reset_canvas():
    st.session_state.canvas_id = 1 - st.session_state.canvas_id

# =========================
# IMAGE PROCESSING (IMPORTANT)
# =========================

if canvas.image_data is not None:

    img = Image.fromarray(canvas.image_data.astype("uint8"))

    # Convert RGBA → grayscale
    img_array = np.array(img)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)

    # Resize to MNIST format
    mnist_img = cv2.resize(gray, (28, 28))

    # SHOW RESULTS (THIS WAS MISSING BEFORE)
    st.subheader("Preview")

    col1, col2 = st.columns(2)

    with col1:
        st.image(img, caption="Canvas (280x280)")

    with col2:
        st.image(mnist_img, caption="MNIST (28x28)")

    # =========================
    # SAVE BUTTON
    # =========================

    if st.button("Save to Google Sheets"):

        if not name:
            st.error("Please enter your name")
            st.stop()

        if is_blank(mnist_img):
            st.error("Canvas is empty!")
            st.stop()

        pixels = mnist_img.flatten().tolist()

        row = [name, int(digit_label)] + pixels

        sheet.append_row(row)

        st.success("Saved successfully ✅")

        # reset canvas ONLY
        reset_canvas()
        st.rerun()
