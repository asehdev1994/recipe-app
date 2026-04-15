import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# =========================
# INIT FIREBASE
# =========================
if not firebase_admin._apps:
    cred = credentials.Certificate(json.loads(st.secrets["FIREBASE_CREDENTIALS"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# RECIPES
# =========================
def load_data():
    doc = db.collection("app_data").document("recipes").get()
    if doc.exists:
        return doc.to_dict()
    return {
        "units": ["g", "kg", "ml", "l", "tsp", "tbsp", "cup", "pcs"],
        "recipes": {}
    }

def save_data(data):
    db.collection("app_data").document("recipes").set(data)

# =========================
# SESSIONS
# =========================
def load_sessions():
    doc = db.collection("app_data").document("sessions").get()
    if doc.exists:
        return doc.to_dict()
    return {}

def save_sessions(data):
    db.collection("app_data").document("sessions").set(data)