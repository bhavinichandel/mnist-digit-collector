import cv2
import gspread
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# ========================================================
# 1. AUTOMATIC GOOGLE SHEETS SETUP
# ========================================================
try:
    # Uses the official direct file shortcut link to connect to Google Sheets
    client = gspread.service_account(filename="google_key.json")
    sheet = client.open("MNIST Dataset").sheet1
except FileNotFoundError:
    st.error("⚠️ Missing 'google_key.json'! Please make sure the file is right next to App.py in your sidebar.")
    st.stop()
except Exception as e:
    st.error(f"Google Connection Error: {e}")
    st.stop()

# Create sheet headers (ONLY ONCE on a blank sheet)
headers = ["name", "label"] + [f"pixel_{i}" for i in range(784)]
data = sheet.get_all_values()

if len(data) == 0:
    sheet.append_row(headers)

# ========================================================
# 2. AUTO-INCREMENT SESSION STATE INITIALIZATION
# ========================================================
# Creates a smart memory block to track your current counting digit
if "current_digit" not in st.session_state:
    st.session_state.current_digit = 0

# Creates a flag tracker to trigger the final completion screen
if "show_thank_you" not in st.session_state:
    st.session_state.show_thank_you = False

# ========================================================
# 3. STREAMLIT USER INTERFACE LAYOUT
# ========================================================
st.title("MNIST Digit Collector")

# Show the massive virtual balloon explosion if they just finished saving a 9
if st.session_state.show_thank_you:
    st.balloons() # Shoots colorful virtual balloons up your monitor screen!
    st.success("## 🎉 Thank you! All 0-9 digits saved successfully!")
    # Turn the flag off so the balloon notification clears out on the next cycle
    st.session_state.show_thank_you = False

# Collector data inputs
name = st.text_input("Enter your name")

# The digital starting label value is driven automatically by session state memory
digit_label = st.number_input(
    "Digit Label (0-9)",
    min_value=0,
    max_value=9,
    value=st.session_state.current_digit, # Injected auto-stepper tracker
    step=1
)

# ========================================================
# 4. CANVAS RESET CONTROL & INTERFACE WHITEBOARD
# ========================================================
if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

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

# ========================================================
# 5. CONVERT IMAGE & VALIDATION PROFILE CONTROLS
# ========================================================
def is_blank(img):
    return np.mean(img) < 5

if canvas_result.image_data is not None:
    img = Image.fromarray(canvas_result.image_data.astype("uint8"))
    st.image(img, caption="Original")

    img_array = np.array(img)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
    
    # 🌟 MULTI-DIGIT SCANNERS: Group pixel shapes to find 00 or 777
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Validation constraint logic check
    if len(contours) > 1:
        st.warning("⚠️ Multiple inputs detected! Please draw only a **single digit** at a time.")
        allow_saving = False
    else:
        allow_saving = True

    mnist_img = cv2.resize(gray, (28, 28))
    st.image(mnist_img, caption="28x28 MNIST Image", width=200)

    # ========================================================
    # 6. SAVE BUTTON (DYNAMIC GREY-OUT ACTION)
    # ========================================================
    # If allow_saving is False (multi-digits found), the button disables itself instantly!
    if st.button("Save to Google Sheets", disabled=not allow_saving):

        if not name:
            st.error("Please enter your name")
            st.stop()

        if is_blank(mnist_img):
            st.error("Canvas is empty! Draw a digit first.")
            st.stop()

        # Unfold the 28x28 picture into a 784 long list array row
        pixels = mnist_img.flatten().tolist()
        row = [name, int(digit_label)] + pixels

        # Ship row directly to the spreadsheet
        sheet.append_row(row)
        st.success(f"Digit {int(digit_label)} Saved to Google Sheets! ✅")

        # 🧠 SMART LOGIC AUTO-STEPPER SWITCH
        if int(digit_label) == 9:
            st.session_state.show_thank_you = True  # Toggle balloon blast trigger
            st.session_state.current_digit = 0     # Cycle number value back to zero
        else:
            # Shift value up by 1 block automatically
            st.session_state.current_digit = int(digit_label) + 1

        # Clear canvas workspace grid layout matrix and rebuild page view variables
        st.session_state.canvas_key += 1
        st.rerun()
