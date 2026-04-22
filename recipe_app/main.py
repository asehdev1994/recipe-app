import streamlit as st

from recipe_app.services.auth import refresh_id_token
from recipe_app.services.auth_cookies import get_cookie_manager
from recipe_app.services.storage import load_data
from recipe_app.ui.auth_ui import show_auth
from recipe_app.ui.sidebar import show_sidebar
from recipe_app.views.add_recipe import show_add_recipe_tab
from recipe_app.views.checklist import show_checklist
from recipe_app.views.manage_recipes import show_manage_recipes_tab
from recipe_app.views.shopping import show_shopping_tab


def main():
    if "view" not in st.session_state:
        st.session_state.view = "main"

    cookies = get_cookie_manager()
    st.session_state.cookies = cookies

    if "user_email" not in st.session_state or not st.session_state.user_email:
        email = cookies.get("user_email")
        if email:
            st.session_state.user_email = email

    if "user_id" not in st.session_state or not st.session_state.user_id:
        refresh_token = cookies.get("refresh_token")

        if refresh_token:
            tokens = refresh_id_token(refresh_token)

            if tokens:
                st.session_state.user_id = tokens["user_id"]
                st.session_state.id_token = tokens["id_token"]
            else:
                cookies["refresh_token"] = ""
                cookies.save()

    if not show_auth():
        st.stop()

    if st.session_state.view == "checklist":
        show_checklist()
        st.stop()

    show_sidebar()

    if "last_user" not in st.session_state:
        st.session_state.last_user = None

    if st.session_state.last_user != st.session_state.user_id:
        st.session_state.data = load_data()
        st.session_state.last_user = st.session_state.user_id

    st.session_state.recipes = st.session_state.data["recipes"]
    st.session_state.units = st.session_state.data["units"]

    if "temp_recipe" not in st.session_state:
        st.session_state.temp_recipe = {}

    if "recipe_scales" not in st.session_state:
        st.session_state.recipe_scales = {}

    if "extra_items" not in st.session_state:
        st.session_state.extra_items = {}

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = None

    st.title("🍳 Recipe & Shopping App")

    tab1, tab2, tab3 = st.tabs([
        "🛒 Shopping List",
        "➕ Add Recipe",
        "📖 Manage Recipes"
    ])

    with tab1:
        show_shopping_tab()

    with tab2:
        show_add_recipe_tab()

    with tab3:
        show_manage_recipes_tab()
