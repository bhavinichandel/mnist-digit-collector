import cv2
import csv
import os
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# ========================================================
# 📂 LOCAL FILE SETUP 
# ========================================================
csv_filename = "mnist_collected_data.csv"

# Creates a local file right inside your project folder if it isn't there
if not os.path.exists(csv_filename):
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        headers = ["name", "label"] + [f"pixel_{i}" for i in range(784)]
        writer.writerow(headers)

# ========================================================
# 🔄 AIRTIGHT SESSION STATE MANAGEMENT
# ========================================================
if "current_digit" not in st.session_state:
    st.session_state.current_digit = 0

if "show_thank_you" not in st.session_state:
    st.session_state.show_thank_you = False

if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

# ========================================================
# 3. STREAMLIT USER INTERFACE LAYOUT
# ========================================================
st.set_page_config(layout="wide") 
st.title("🔢 MNIST Digit Collector")

if st.session_state.show_thank_you:
    st.balloons() 
    st.success("## 🎉 Thank you! All 0-9 digits saved successfully!")
    st.session_state.show_thank_you = False

# Sidebar for clean, attractive layout handling
with st.sidebar:
    st.header("👤 User Registration")
    name = st.text_input("Enter your name")
    
    st.markdown("---")
    st.markdown("### 🎯 Current Target")
    # 🚨 THE PERMANENT FIX: Display as a read-only target metric.
    # This prevents manual manipulation and secures your data stream completely.
    st.metric(label="Draw this number next", value=st.session_state.current_digit)
    st.info(f"Please draw the digit: **{st.session_state.current_digit}**")

# Use side-by-side columns to make it attractive and avoid vertical stacking
col1, col2 = st.columns(2)

with col1:
    st.subheader("✍️ Draw Inside The Box")
    canvas_result = st_canvas(
        fill_color="black",
        stroke_width=15,
        stroke_color="white",
        background_color="black",
        height=280,
        width=280,
        drawing_mode="freedraw",
        key=f"canvas_{st.session_state.canvas_key}",
        update_streamlit=True,
    )

# ========================================================
# 4. CONVERT IMAGE & VALIDATION PROFILE CONTROLS
# ========================================================
def is_blank(img):
    return np.mean(img) < 5

if canvas_result.image_data is not None:
    img = Image.fromarray(canvas_result.image_data.astype("uint8"))
    img_array = np.array(img)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
    
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 1:
        st.warning("⚠️ Multiple inputs detected! Please draw only a **single digit** at a time.")
        allow_saving = False
    else:
        allow_saving = True

    mnist_img = cv2.resize(gray, (28, 28))
    
    with col2:
        st.subheader("🔍 Dataset Real-time Render")
        st.image(mnist_img, caption=f"Processed 28x28 rendering for digit {st.session_state.current_digit}", width=200)

    # ========================================================
    # 5. TRANSACT DATA TO DISK
    # ========================================================
    st.markdown("---")
    if st.button("Save Data", disabled=not allow_saving, use_container_width=True):

        if not name.strip():
            st.error("Please enter your name")
            st.stop()

        if is_blank(mnist_img):
            st.error("Canvas is empty! Draw a digit first.")
            st.stop()

        # Capture target directly from state variables to prevent sync delays
        target_to_save = int(st.session_state.current_digit)

        # 🚨 THE AIRTIGHT DUPLICATE CHECK
        try:
            df = pd.read_csv(csv_filename)
            df['name'] = df['name'].astype(str).str.strip().str.lower()
            df['label'] = df['label'].astype(int)
            
            clean_name = name.strip().lower()

            # Queries name matching combined with the current exact session number value
            duplicate_exists = not df[(df['name'] == clean_name) & (df['label'] == target_to_save)].empty
            
            if duplicate_exists:
                st.error("🚨 Duplicate number not allowed")
                st.stop()
        except Exception:
            pass

        # Unfold the 28x28 picture into a 784 long list array row
        pixels = mnist_img.flatten().tolist()
        row = [name.strip(), target_to_save] + pixels

        # Append data row straight into the local file
        with open(csv_filename, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)
            
        st.success(f"Digit {target_to_save} Saved successfully to '{csv_filename}'! ✅")
        
        # 🔄 SECURE AUTO INCREMENT PROGRESSION
        if target_to_save == 9:
            st.session_state.show_thank_you = True  
            st.session_state.current_digit = 0     
        else:
            st.session_state.current_digit = target_to_save + 1
        
        # Completely clear the canvas drawing frame area cleanly
        st.session_state.canvas_key += 1
        st.rerun()
