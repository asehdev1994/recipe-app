import streamlit as st
from storage import delete_user


def show_sidebar():

    st.sidebar.markdown("### 👤 User")
    email = st.session_state.get("user_email") or st.session_state.user_id
    st.sidebar.markdown(f"**Current user:** `{email}`")

    if st.sidebar.button("🚪 Logout"):
        cookies = st.session_state.cookies
        cookies["refresh_token"] = ""
        cookies.save()
        
        st.session_state.user_id = None
        st.session_state.id_token = None
        st.session_state.user_email = None
        
        st.rerun()

    # DELETE USER
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

    if st.sidebar.button("🗑 Delete User"):
        st.session_state.confirm_delete = True

    if st.session_state.confirm_delete:
        st.sidebar.warning("Are you sure you want to delete this user?")

        if st.sidebar.button("Confirm Delete"):
            delete_user(st.session_state.user_id)
            cookies = st.session_state.cookies
            cookies["refresh_token"] = ""
            cookies.save()

            st.session_state.user_id = None
            st.session_state.confirm_delete = False
            st.session_state.user_email = None

            for key in ["data", "recipes", "units"]:
                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()