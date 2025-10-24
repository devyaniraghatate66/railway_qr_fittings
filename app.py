import streamlit as st
import qrcode
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from sqlalchemy import create_engine, Column, String, Integer, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from PIL import Image
import pandas as pd
import os
import urllib.parse

# -----------------------------
# Database Setup (MySQL)
# -----------------------------
# Escape special characters in password (e.g. @, #, !)
password = urllib.parse.quote_plus("Devyani%@4010")
DATABASE_URL = f"mysql+mysqlconnector://root:{password}@localhost:3306/railways_db"

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------
# Define Fitting Table Model
# -----------------------------
class Fitting(Base):
    __tablename__ = "fittings"   # ✅ fixed (double underscores)

    fitting_id = Column(String(50), primary_key=True, index=True)
    item_type = Column(String(100))
    metal_type = Column(String(50))
    vendor_name = Column(String(100))
    lot_number = Column(String(100))
    date_of_manufacture = Column(Date)
    date_of_supply = Column(Date)
    warranty_years = Column(Integer)
    expiry_date = Column(Date)
    initial_inspection = Column(Date)
    inspection_frequency_months = Column(Integer)
    next_inspection = Column(Date)
    location = Column(String(200))
    track_name = Column(String(200))
    remarks = Column(Text)
    created_at = Column(String(100))

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# -----------------------------
# QR Code Generator
# -----------------------------
def generate_qr_code(data_str):
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="Railway Track Fittings QR Generator", layout="centered")
st.title("🚆 Indian Railways - Track Fittings QR Generator")

# --------------------
