import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from recipe_app.services.auth import refresh_id_token

def ensure_valid_token():
    cookies = st.session_state.get("cookies")

    if not cookies:
        return

    refresh_token = cookies.get("refresh_token")

    if not refresh_token:
        return

    tokens = refresh_id_token(refresh_token)

    if tokens:
        st.session_state.id_token = tokens["id_token"]

        # 🔁 Update refresh token if rotated
        if tokens.get("refresh_token"):
            cookies["refresh_token"] = tokens["refresh_token"]
            cookies.save()


def _using_firestore_emulator():
    return bool(os.getenv("FIRESTORE_EMULATOR_HOST"))


def _get_project_id():
    env_project_id = os.getenv("FIREBASE_PROJECT_ID")
    if env_project_id:
        return env_project_id

    firebase_credentials = st.secrets.get("FIREBASE_CREDENTIALS")
    if firebase_credentials:
        return firebase_credentials["project_id"]

    raise KeyError("FIREBASE_PROJECT_ID is not configured")


def _get_db():
    if not firebase_admin._apps:
        if _using_firestore_emulator():
            firebase_admin.initialize_app(options={"projectId": _get_project_id()})
        else:
            firebase_dict = dict(st.secrets["FIREBASE_CREDENTIALS"])

            # Fix private key formatting
            firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")

            cred = credentials.Certificate(firebase_dict)
            firebase_admin.initialize_app(cred)

    return firestore.client()


def _get_users_collection():
    return _get_db().collection("users")

# =========================
# USER HELPERS
# =========================
def _get_user_ref():
    ensure_valid_token()

    user_id = st.session_state.get("user_id")

    if not user_id:
        raise Exception("User not authenticated")
    
    ref = _get_users_collection().document(user_id)

    # 🔥 Ensure document actually exists (CRITICAL FIX)
    if not ref.get().exists:
        ref.set({"created": True})

    return ref

def get_all_users():
    users_ref = _get_users_collection().stream()
    return sorted([doc.id for doc in users_ref])

def delete_user(user_id):
    _get_users_collection().document(user_id).delete()

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
