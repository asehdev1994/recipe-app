import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

print("NEW STORAGE VERSION LOADED")
print("DELETE USER FUNCTION AVAILABLE")

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
    user_id = st.session_state.get("user_id")

    if not user_id:
        raise Exception("User not authenticated")
    
    ref = db.collection("users").document(user_id)

    # 🔥 Ensure document actually exists (CRITICAL FIX)
    if not ref.get().exists:
        ref.set({"created": True})

    return ref

def get_all_users():
    users_ref = db.collection("users").stream()
    return sorted([doc.id for doc in users_ref])

def delete_user(user_id):
    db.collection("users").document(user_id).delete()

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