import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
from PIL import Image
import cv2
import gspread
from google.oauth2.service_account import Credentials

# =========================
# GOOGLE SHEETS (CACHED)
# =========================
@st.cache_resource
def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["google"],
        scopes=scopes
    )

    client = gspread.authorize(creds)
    return client.open("MNIST Dataset").sheet1

sheet = get_sheet()

# =========================
# SESSION STATE
# =========================
if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

if "digit" not in st.session_state:
    st.session_state.digit = 0

# =========================
# UI
# =========================
st.title("MNIST Digit Collector")

name = st.text_input("Enter your name")

st.write("Current Label:", st.session_state.digit)

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
# IMAGE PROCESSING
# =========================
def is_blank(img):
    return np.mean(img) < 2

if canvas_result.image_data is not None:

    raw_img = canvas_result.image_data

    # ✅ FIX: proper blank check BEFORE processing
    if raw_img is None:
        st.stop()

    if np.mean(raw_img) < 2:
        st.warning("Draw a digit first")
    else:

        img = Image.fromarray(raw_img.astype("uint8"))
        img_array = np.array(img)

        # remove alpha channel if exists
        if img_array.shape[-1] == 4:
            img_array = img_array[:, :, :3]

        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        mnist_img = cv2.resize(gray, (28, 28))

        st.image(mnist_img, caption="28x28 MNIST Image", width=200)

        # =========================
        # SAVE BUTTON (SAFE FORM)
        # =========================
        with st.form("save_form"):

            submitted = st.form_submit_button("Save to Google Sheets")

            if submitted:

                if not name.strip():
                    st.error("Enter your name")
                    st.stop()

                if np.mean(raw_img) < 2:
                    st.error("Draw a digit first")
                    st.stop()

                pixels = mnist_img.flatten().tolist()

                # ✅ FIX: always use session_state digit
                row = [name, st.session_state.digit] + pixels

                sheet.append_row(row)

                st.success("Saved to Google Sheets ✅")

                # =========================
                # AUTO-INCREMENT (FIXED)
                # =========================
                st.session_state.digit = (st.session_state.digit + 1) % 10

                # =========================
                # RESET CANVAS
                # =========================
                st.session_state.canvas_key += 1

                st.rerun()
