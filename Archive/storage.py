import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

print("🔥 NEW STORAGE VERSION LOADED")

# =========================
# INIT FIREBASE
# =========================
if not firebase_admin._apps:
    firebase_dict = dict(st.secrets["FIREBASE_CREDENTIALS"])

    # Fix private key formatting
    firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")

    cred = credentials.Certificate(firebase_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================
# USER HELPERS
# =========================
def _get_user_ref():
    user_id = st.session_state.get("user_id", "default")
    ref = db.collection("users").document(user_id)

    # 🔥 Ensure document actually exists (CRITICAL FIX)
    if not ref.get().exists:
        ref.set({"created": True})

    return ref

def get_all_users():
    users_ref = db.collection("users").stream()
    return sorted([doc.id for doc in users_ref])

# =========================
# RECIPES
# =========================
def load_data():
    ref = _get_user_ref().collection("data").document("recipes")
    doc = ref.get()

    if doc.exists:
        return doc.to_dict()

    return {
        "units": ["g", "kg", "ml", "l", "tsp", "tbsp", "cup", "pcs"],
        "recipes": {}
    }

def save_data(data):
    ref = _get_user_ref().collection("data").document("recipes")
    ref.set(data)

# =========================
# SESSIONS
# =========================
def load_sessions():
    ref = _get_user_ref().collection("data").document("sessions")
    doc = ref.get()

    if doc.exists:
        return doc.to_dict()

    return {}

def save_sessions(data):
    ref = _get_user_ref().collection("data").document("sessions")
    ref.set(data)