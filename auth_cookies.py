# auth_cookies.py

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

def _get_cookie_password():
    return st.secrets["cookie_password"]

def get_cookie_manager():
    cookies = EncryptedCookieManager(
        prefix="recipe_app_",
        password=_get_cookie_password(),
    )

    if not cookies.ready():
        st.stop()

    return cookies
