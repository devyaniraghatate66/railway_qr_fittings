# app.py - Railway Track Fittings QR Generator with Supabase
import streamlit as st
import qrcode
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
from supabase import create_client

# -------------------------------------------------------
# 🔐 Supabase Setup (Hardcoded)
# -------------------------------------------------------
SUPABASE_URL = "https://jfuleffsjabisgowwydk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpmdWxlZmZzamFiaXNnb3d3eWRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMDA0OTMsImV4cCI6MjA3Njg3NjQ5M30.AIWy21xt3nE6JVosKF7YsKkA-5MujsRGvzpttXRvPjY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------------------
# 🎨 Streamlit App Setup
# -------------------------------------------------------
st.set_page_config(page_title="Railway Track Fittings QR Generator", layout="centered")
st.title("🚆 Indian Railways - Track Fittings QR Generator")

# -------------------------------------------------------
# QR Code Generator
# -------------------------------------------------------
def generate_qr_code(data_str: str) -> Image.Image:
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(data_str)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

# -------------------------------------------------------
# Default Session State
# -------------------------------------------------------
defaults = {
    "item_type": "Elastic Rail Clip",
    "metal_type": "Steel",
    "vendor_name": "",
    "lot_number": "",
    "date_of_manufacture": datetime.today().date(),
    "date_of_supply": datetime.today().date(),
    "warranty_years": 10,
    "initial_inspection": datetime.today().date(),
    "inspection_frequency": 6,
    "location": "",
    "track_name": "",
    "remarks": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------------------------------------------
# Fitting Input Form
# -------------------------------------------------------
with st.form("qr_form"):
    st.subheader("Enter Fitting Details")

    st.session_state["item_type"] = st.selectbox(
        "Item Type", ["Elastic Rail Clip", "Rail Pad", "Liner", "Sleeper"], 
        index=["Elastic Rail Clip","Rail Pad","Liner","Sleeper"].index(st.session_state["item_type"])
    )
    st.session_state["metal_type"] = st.selectbox(
        "Metal Type", ["Steel", "Iron", "Alloy"], 
        index=["Steel", "Iron", "Alloy"].index(st.session_state["metal_type"])
    )
    st.session_state["vendor_name"] = st.text_input("Vendor / Manufacturer Name", value=st.session_state["vendor_name"])
    st.session_state["lot_number"] = st.text_input("Vendor Lot / Batch Number", value=st.session_state["lot_number"])
    st.session_state["date_of_manufacture"] = st.date_input("Date of Manufacture", value=st.session_state["date_of_manufacture"])
    st.session_state["date_of_supply"] = st.date_input("Date of Supply", value=st.session_state["date_of_supply"])
    st.session_state["warranty_years"] = st.number_input("Warranty Period (Years)", min_value=1, max_value=20, value=st.session_state["warranty_years"])
    st.session_state["initial_inspection"] = st.date_input("Initial Inspection Date", value=st.session_state["initial_inspection"])
    st.session_state["inspection_frequency"] = st.number_input("Inspection Frequency (Months)", min_value=1, value=st.session_state["inspection_frequency"])
    st.session_state["location"] = st.text_input("Location / Track Section ID", value=st.session_state["location"])
    st.session_state["track_name"] = st.text_input("Full Railway Station / Track Name", value=st.session_state["track_name"])
    st.session_state["remarks"] = st.text_area("Remarks / Notes", value=st.session_state["remarks"])

    submitted = st.form_submit_button("Generate QR")

# -------------------------------------------------------
# Handle Submission
# -------------------------------------------------------
if submitted:
    try:
        # Generate unique fitting ID
        fitting_id = str(uuid.uuid4())
        expiry_date = st.session_state["date_of_supply"] + timedelta(days=st.session_state["warranty_years"]*365)
        next_inspection = st.session_state["initial_inspection"] + timedelta(days=st.session_state["inspection_frequency"]*30)

        # Prepare data to insert into Supabase
        fitting_data = {
            "fitting_id": fitting_id,
            "item_type": st.session_state["item_type"],
            "metal_type": st.session_state["metal_type"],
            "vendor_name": st.session_state["vendor_name"],
            "lot_number": st.session_state["lot_number"],
            "date_of_manufacture": st.session_state["date_of_manufacture"].isoformat(),
            "date_of_supply": st.session_state["date_of_supply"].isoformat(),
            "warranty_years": st.session_state["warranty_years"],
            "expiry_date": expiry_date.isoformat(),
            "initial_inspection": st.session_state["initial_inspection"].isoformat(),
            "inspection_frequency_months": st.session_state["inspection_frequency"],
            "next_inspection": next_inspection.isoformat(),
            "location": st.session_state["location"],
            "track_name": st.session_state["track_name"],
            "remarks": st.session_state["remarks"],
            "created_at": datetime.now().isoformat()
        }

        # Insert into Supabase
        supabase.table("fittings").insert(fitting_data).execute()

        # Generate QR Code
        qr_data = f"https://railways-tracking-system.gov/fitting/{fitting_id}"
        img = generate_qr_code(qr_data)

        st.success("✅ QR Code Generated and Saved to Supabase!")
        st.image(img, caption="Scan this QR to fetch fitting details", use_container_width=True)

        # Download QR Code
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        st.download_button(
            label="📥 Download QR Code",
            data=buf,
            file_name=f"qr_{fitting_id}.png",
            mime="image/png"
        )

        # Reset session state
        for key, value in defaults.items():
            st.session_state[key] = value

    except Exception as e:
        st.error(f"❌ Error: {e}")
