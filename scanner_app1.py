# scanner_app1.py
import streamlit as st
from PIL import Image
import cv2
import numpy as np
from datetime import date
from supabase import create_client

# -------------------------------------------------------
# 🔐 Supabase Setup (Hardcoded)
# -------------------------------------------------------
SUPABASE_URL = "https://jfuleffsjabisgowwydk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpmdWxlZmZzamFiaXNnb3d3eWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMDA0OTMsImV4cCI6MjA3Njg3NjQ5M30.AIWy21xt3nE6JVosKF7YsKkA-5MujsRGvzpttXRvPjY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------------------
# 🎨 Streamlit UI Setup
# -------------------------------------------------------
st.set_page_config(page_title="Railway Fittings QR Scanner", layout="centered")
st.title("📱 Indian Railways - QR Fitting Scanner")
st.write("Scan or upload a QR code to retrieve fitting details.")

# -------------------------------------------------------
# ⚙️ QR Processing Function using OpenCV
# -------------------------------------------------------
def process_qr(img: Image.Image) -> str | None:
    """Decode QR code from an image using OpenCV and extract fitting ID."""
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(cv_img)
    if data:
        fitting_id = data.split("fitting/")[-1] if "fitting/" in data else data
        return fitting_id
    return None

# -------------------------------------------------------
# 🖼️ Input Selection
# -------------------------------------------------------
option = st.radio("Select Input Method", ["Camera", "Upload QR Image"], index=0)
fitting_id = None

if option == "Camera":
    camera_input = st.camera_input("Scan QR Code with Camera")
    if camera_input:
        img = Image.open(camera_input)
        fitting_id = process_qr(img)

elif option == "Upload QR Image":
    file_input = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])
    if file_input:
        img = Image.open(file_input)
        fitting_id = process_qr(img)

# -------------------------------------------------------
# 🔍 Fetch Data from Supabase
# -------------------------------------------------------
if fitting_id:
    st.success(f"✅ QR Code Detected! Fitting ID: {fitting_id}")
    
    response = supabase.table("fittings").select("*").eq("fitting_id", fitting_id).execute()
    
    if response.data:
        fitting = response.data[0]

        st.subheader("🔎 Fitting Details")
        details = {
            "Item Type": fitting.get("item_type"),
            "Metal Type": fitting.get("metal_type"),
            "Vendor Name": fitting.get("vendor_name"),
            "Lot Number": fitting.get("lot_number"),
            "Date of Manufacture": fitting.get("date_of_manufacture"),
            "Date of Supply": fitting.get("date_of_supply"),
            "Warranty (Years)": fitting.get("warranty_years"),
            "Warranty Expiry": fitting.get("expiry_date"),
            "Initial Inspection": fitting.get("initial_inspection"),
            "Inspection Frequency (Months)": fitting.get("inspection_frequency_months"),
            "Next Inspection Due": fitting.get("next_inspection"),
            "Location / Track ID": fitting.get("location"),
            "Railway Station / Track Name": fitting.get("track_name"),
            "Remarks": fitting.get("remarks")
        }
        for key, value in details.items():
            st.write(f"**{key}:** {value}")

        # -------------------------------------------------------
        # 🚨 Alerts Section
        # -------------------------------------------------------
        today = date.today()
        alerts = []

        expiry_date = fitting.get("expiry_date")
        next_insp = fitting.get("next_inspection")
        supply_date = fitting.get("date_of_supply")

        if expiry_date and today > date.fromisoformat(expiry_date):
            alerts.append("⚠️ Warranty Expired!")
        if next_insp and today > date.fromisoformat(next_insp):
            alerts.append("🔧 Inspection Overdue!")
        if supply_date and (today - date.fromisoformat(supply_date)).days > (10 * 365):
            alerts.append("⛔ Service Life (10 years) Exceeded!")

        if alerts:
            st.error(" | ".join(alerts))
        else:
            st.success("✅ All Good. No issues found.")
    else:
        st.error("❌ No record found for this Fitting ID.")
else:
    st.info("📷 Please scan a QR code or upload an image to continue.")
