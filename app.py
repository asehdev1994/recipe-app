import streamlit as st
from storage import load_data
from auth_ui import show_auth
from auth_cookies import get_cookie_manager
from auth import refresh_id_token
from views.checklist import show_checklist
from views.shopping import show_shopping_tab
from views.add_recipe import show_add_recipe_tab
from views.manage_recipes import show_manage_recipes_tab
from sidebar import show_sidebar

# =========================
# VIEW STATE
# =========================
if "view" not in st.session_state:
    st.session_state.view = "main"

# =========================
# AUTO LOGIN
# =========================
cookies = get_cookie_manager()
st.session_state.cookies = cookies

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

# =========================
# AUTH
# =========================

if not show_auth():
    st.stop()

# =========================
# Routing
# =========================
    
if st.session_state.view == "checklist":
    show_checklist()
    st.stop()

# =========================
# SIDEBAR
# =========================
    
show_sidebar()

# =========================
# LOAD DATA
# =========================
if "last_user" not in st.session_state:
    st.session_state.last_user = None

if st.session_state.last_user != st.session_state.user_id:
    st.session_state.data = load_data()
    st.session_state.last_user = st.session_state.user_id

st.session_state.recipes = st.session_state.data["recipes"]
st.session_state.units = st.session_state.data["units"]

# =========================
# INIT STATE
# =========================
if "temp_recipe" not in st.session_state:
    st.session_state.temp_recipe = {}

if "recipe_scales" not in st.session_state:
    st.session_state.recipe_scales = {}

if "extra_items" not in st.session_state:
    st.session_state.extra_items = {}

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None

# =========================
# UI
# =========================
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