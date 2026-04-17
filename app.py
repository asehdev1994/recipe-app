import streamlit as st
from storage import load_data, delete_user
from auth_ui import show_auth
from views.checklist import show_checklist
from views.shopping import show_shopping_tab
from views.add_recipe import show_add_recipe_tab
from views.manage_recipes import show_manage_recipes_tab

# =========================
# VIEW STATE
# =========================
if "view" not in st.session_state:
    st.session_state.view = "main"

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