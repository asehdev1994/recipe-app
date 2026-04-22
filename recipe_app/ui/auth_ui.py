import streamlit as st
from recipe_app.services.auth import sign_in, sign_up, send_password_reset


def show_auth():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if st.session_state.user_id:
        return True

    st.title("🔐 Login")

    mode = st.radio("Choose", ["Login", "Sign Up"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # =========================
    # SUBMIT (LOGIN / SIGNUP)
    # =========================
    if st.button("Submit"):

        if mode == "Login":
            res = sign_in(email, password)
        else:
            res = sign_up(email, password)

        if "localId" in res:
            st.session_state.user_id = res["localId"]
            st.session_state.id_token = res["idToken"]

            email = res.get("email", "")
            st.session_state.user_email = email

            cookies = st.session_state.cookies
            cookies["refresh_token"] = res.get("refreshToken", "")
            cookies["user_email"] = email
            cookies.save()

            st.success("Logged in!")
            st.rerun()
        else:
            st.error(res.get("error", {}).get("message", "Auth failed"))

    # =========================
    # PASSWORD RESET (LOGIN ONLY)
    # =========================
    if mode == "Login":
        if st.button("Forgot Password?"):
            if email:
                res = send_password_reset(email)

                if "error" not in res:
                    st.success("Password reset email sent (if account exists).")
                else:
                    st.error(
                        res.get("error", {}).get("message", "Error sending reset email")
                    )
            else:
                st.warning("Please enter your email first")

    return False
