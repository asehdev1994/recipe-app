import streamlit as st
from storage import delete_user


def show_sidebar():

    st.sidebar.markdown("### 👤 User")
    st.sidebar.markdown(f"**Current user:** `{st.session_state.user_id}`")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.user_id = None
        st.session_state.id_token = None
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

            st.session_state.user_id = None
            st.session_state.confirm_delete = False

            for key in ["data", "recipes", "units"]:
                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()