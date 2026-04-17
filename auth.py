import requests
import streamlit as st

API_KEY = st.secrets["FIREBASE_API_KEY"]

def sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    return requests.post(url, json=payload).json()


def sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    return requests.post(url, json=payload).json()
    
def sign_in_anonymous():
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "returnSecureToken": True
    }
    return requests.post(url, json=payload).json()   

def send_password_reset(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
    
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }

    return requests.post(url, json=payload).json()
    
def refresh_id_token(refresh_token):
    url = f"https://securetoken.googleapis.com/v1/token?key={API_KEY}"

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