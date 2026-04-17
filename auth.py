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