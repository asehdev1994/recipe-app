import streamlit as st
from auth import sign_in, sign_up


def show_auth():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if st.session_state.user_id:
        return True

    st.title("🔐 Login")

    mode = st.radio("Choose", ["Login", "Sign Up"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):

        if mode == "Login":
            res = sign_in(email, password)
        else:
            res = sign_up(email, password)

        if "localId" in res:
            st.session_state.user_id = res["localId"]
            st.session_state.id_token = res["idToken"]
            st.success("Logged in!")
            st.rerun()
        else:
            st.error(res.get("error", {}).get("message", "Auth failed"))

    return False