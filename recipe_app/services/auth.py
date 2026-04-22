import os

import requests
import streamlit as st

def _get_api_key():
    env_api_key = os.getenv("FIREBASE_API_KEY")
    if env_api_key:
        return env_api_key

    return st.secrets["FIREBASE_API_KEY"]


def _using_auth_emulator():
    return bool(os.getenv("FIREBASE_AUTH_EMULATOR_URL") or os.getenv("FIREBASE_AUTH_EMULATOR_HOST"))


def _get_auth_base_url():
    emulator_url = os.getenv("FIREBASE_AUTH_EMULATOR_URL")
    if emulator_url:
        return emulator_url.rstrip("/")

    emulator_host = os.getenv("FIREBASE_AUTH_EMULATOR_HOST")
    if emulator_host:
        return f"http://{emulator_host}"

    return "https://identitytoolkit.googleapis.com"


def _get_securetoken_base_url():
    if _using_auth_emulator():
        return f"{_get_auth_base_url()}/securetoken.googleapis.com"

    return "https://securetoken.googleapis.com"


def _build_identity_toolkit_url(path):
    if _using_auth_emulator():
        base = f"{_get_auth_base_url()}/identitytoolkit.googleapis.com/v1"
    else:
        base = "https://identitytoolkit.googleapis.com/v1"

    return f"{base}/{path}?key={_get_api_key()}"


def _build_securetoken_url(path):
    return f"{_get_securetoken_base_url()}/v1/{path}?key={_get_api_key()}"

def sign_up(email, password):
    url = _build_identity_toolkit_url("accounts:signUp")
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    return requests.post(url, json=payload).json()


def sign_in(email, password):
    url = _build_identity_toolkit_url("accounts:signInWithPassword")
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    return requests.post(url, json=payload).json()
    
def sign_in_anonymous():
    url = _build_identity_toolkit_url("accounts:signUp")
    payload = {
        "returnSecureToken": True
    }
    return requests.post(url, json=payload).json()   

def send_password_reset(email):
    url = _build_identity_toolkit_url("accounts:sendOobCode")
    
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }

    return requests.post(url, json=payload).json()
    
def refresh_id_token(refresh_token):
    url = _build_securetoken_url("token")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        res = response.json()
        return {
            "id_token": res["id_token"],
            "refresh_token": res["refresh_token"],
            "user_id": res["user_id"],
        }

    return None
