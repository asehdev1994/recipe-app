import streamlit as st
import uuid
import socket
from mobile_view import render_mobile
from storage import load_data, save_data, load_sessions, save_sessions, delete_user
from utils import format_qty, generate_shopping_list, generate_qr

# =========================
# AUTO-SET USER FROM URL
# =========================
query_params = st.query_params

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# If user passed in URL, use it
if not st.session_state.user_id and "user" in query_params:
    st.session_state.user_id = query_params["user"]

# =========================
# HELPER: BASE URL
# =========================
def get_base_url():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return f"http://{local_ip}:8501"

# =========================
# USER HANDLING (REQUIRED + RADIO)
# =========================
from storage import get_all_users

# -------------------------
# INIT
# -------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

user_list = get_all_users()

# -------------------------
# FORCE USER SELECTION
# -------------------------
if not st.session_state.user_id:

    st.title("👤 Select or Create User")

    mode = st.radio(
        "Choose option",
        ["Select existing user", "Create new user"]
    )

    selected_user = None
    new_user_input = ""

    # -------------------------
    # EXISTING USER MODE
    # -------------------------
    if mode == "Select existing user":
        if user_list:
            selected_user = st.selectbox(
                "Select user",
                options=user_list
            )
        else:
            st.info("No users yet — create one")

    # -------------------------
    # NEW USER MODE
    # -------------------------
    else:
        new_user_input = st.text_input("Enter new user")

    # -------------------------
    # CONTINUE BUTTON
    # -------------------------
    if st.button("Continue"):

        if mode == "Create new user":
            new_user = new_user_input.strip().lower()
        else:
            new_user = selected_user

        if new_user:
            st.session_state.user_id = new_user
            st.rerun()
        else:
            st.warning("Please select or enter a user")

    # 🚨 STOP rest of app
    st.stop()

# -------------------------
# NORMAL APP (USER SET)
# -------------------------
st.sidebar.markdown("### 👤 User")
st.sidebar.markdown(f"**Current user:** `{st.session_state.user_id}`")

# Optional: allow switching user
if st.sidebar.button("🔄 Switch User"):
    st.session_state.user_id = None
    st.rerun()

# -------------------------
# DELETE USER
# -------------------------
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

if st.sidebar.button("🗑 Delete User"):
    st.session_state.confirm_delete = True

if st.session_state.confirm_delete:
    st.sidebar.warning("Are you sure you want to delete this user?")

    if st.sidebar.button("Confirm Delete"):
        
        delete_user(st.session_state.user_id)

        # Reset app state
        st.session_state.user_id = None
        st.session_state.confirm_delete = False

        # Clear cached data
        for key in ["data", "recipes", "units"]:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()

# =========================
# INIT STATE
# =========================
if "last_user" not in st.session_state:
    st.session_state.last_user = None

if st.session_state.last_user != st.session_state.user_id:
    st.session_state.data = load_data()
    st.session_state.last_user = st.session_state.user_id

st.session_state.recipes = st.session_state.data["recipes"]
st.session_state.units = st.session_state.data["units"]

if "temp_recipe" not in st.session_state:
    st.session_state.temp_recipe = {}

if "new_unit_input" not in st.session_state:
    st.session_state.new_unit_input = ""

if "recipe_scales" not in st.session_state:
    st.session_state.recipe_scales = {}

if "shopping_sessions" not in st.session_state:
    st.session_state.shopping_sessions = {}

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None

# =========================
# MOBILE MODE
# =========================
if st.query_params.get("mobile") == "1":
    render_mobile()
    st.stop()

# =========================
# UI
# =========================
st.title("🍳 Recipe & Shopping App")

tab1, tab2, tab3 = st.tabs([
    "🛒 Shopping List",
    "➕ Add Recipe",
    "📖 Manage Recipes"
])

# =========================
# TAB 1
# =========================
with tab1:

    selected = st.multiselect(
        "Choose recipes:",
        list(st.session_state.recipes.keys())
    )

    if selected:
        for r in selected:
            if r not in st.session_state.recipe_scales:
                st.session_state.recipe_scales[r] = 1

            st.session_state.recipe_scales[r] = st.number_input(
                f"{r} scale",
                min_value=1,
                step=1,
                value=st.session_state.recipe_scales[r],
                key=f"scale_{r}"
            )

    if "extra_items" not in st.session_state:
        st.session_state.extra_items = {}

    st.markdown("### ➕ Add Extra Items")

    col1, col2, col3 = st.columns(3)

    with col1:
        extra_name = st.text_input("Item name", key="extra_name")

    with col2:
        extra_qty = st.number_input("Qty", min_value=0.0, step=1.0, key="extra_qty")

    with col3:
        extra_unit_choice = st.selectbox(
            "Unit",
            st.session_state.units + ["➕ Add new unit"],
            key="extra_unit"
        )

    extra_unit = None

    if extra_unit_choice == "➕ Add new unit":
        new_unit_input = st.text_input("New unit", key="extra_new_unit")

        if st.button("Add unit (extra)"):
            new_unit = new_unit_input.strip().lower()

            if new_unit and new_unit not in st.session_state.units:
                st.session_state.units.append(new_unit)
                st.session_state.data["units"] = st.session_state.units
                save_data(st.session_state.data)

                # reload
                st.session_state.data = load_data()
                st.session_state.units = st.session_state.data["units"]

                st.success(f"Added unit: {new_unit}")
                st.rerun()
    else:
        extra_unit = extra_unit_choice

    if st.button("➕ Add Extra Item"):
        if extra_name and extra_unit:
            st.session_state.extra_items[extra_name] = {
                "qty": extra_qty,
                "unit": extra_unit
            }
            st.success(f"Added {extra_name}")
            st.rerun()

    if st.session_state.extra_items:
        st.markdown("#### Extra Items")

        for k, v in st.session_state.extra_items.items():
            col1, col2 = st.columns([4,1])

            with col1:
                st.write(f"{k}: {format_qty(v['qty'])} {v['unit']}")

            with col2:
                if st.button("❌", key=f"remove_extra_{k}"):
                    del st.session_state.extra_items[k]
                    st.rerun()

    if selected or st.session_state.extra_items:

        shopping = generate_shopping_list(
            selected,
            st.session_state.recipes,
            st.session_state.recipe_scales
        )

        for k, v in st.session_state.extra_items.items():
            if k not in shopping:
                shopping[k] = v
            else:
                shopping[k]["qty"] += v["qty"]

        st.subheader("Shopping List")

        for k, v in shopping.items():
            st.write(f"{k}: {format_qty(v['qty'])} {v['unit']}")

        if st.button("📱 Generate Mobile Checklist"):

            session_id = str(uuid.uuid4())

            sessions = load_sessions()
            sessions[session_id] = shopping
            save_sessions(sessions)

            BASE_URL = "https://recipe-app-hrbywsan2sa9wyrrzvfox8.streamlit.app/"
            user = st.session_state.get("user_id", "default")
            url = f"{BASE_URL}/?mobile=1&id={session_id}&user={user}"

            qr = generate_qr(url)

            st.success("Open shopping list")
            st.markdown(f"[👉 Open Shopping List]({url})")
            st.image(qr, use_container_width=True)
            st.code(url)

# =========================
# TAB 2
# =========================
with tab2:
    st.subheader("Create recipe")

    recipe_name = st.text_input("Recipe name")
    instructions = st.text_area("Instructions")

    ingredient_name = st.text_input("Ingredient")
    qty = st.number_input("Quantity", min_value=0.0, step=1.0)

    unit_choice = st.selectbox(
        "Unit",
        st.session_state.units + ["➕ Add new unit"]
    )

    unit = None

    if unit_choice == "➕ Add new unit":
        st.session_state.new_unit_input = st.text_input(
            "New unit",
            value=st.session_state.new_unit_input
        )

        if st.button("Add unit"):
            new_unit = st.session_state.new_unit_input.strip().lower()

            if new_unit and new_unit not in st.session_state.units:
                st.session_state.units.append(new_unit)
                st.session_state.data["units"] = st.session_state.units
                save_data(st.session_state.data)

                # reload
                st.session_state.data = load_data()
                st.session_state.units = st.session_state.data["units"]

                st.session_state.new_unit_input = ""
                st.success("Unit added")
                st.rerun()
    else:
        unit = unit_choice

    if st.button("Add ingredient"):
        if ingredient_name and unit:
            st.session_state.temp_recipe[ingredient_name] = {
                "qty": qty,
                "unit": unit
            }

    st.json(st.session_state.temp_recipe)

    if st.button("Save recipe"):
        if recipe_name and st.session_state.temp_recipe:
            st.session_state.recipes[recipe_name] = {
                "ingredients": st.session_state.temp_recipe,
                "instructions": instructions
            }

            st.session_state.data["recipes"] = st.session_state.recipes
            save_data(st.session_state.data)

            # 🔥 reload
            st.session_state.data = load_data()
            st.session_state.recipes = st.session_state.data["recipes"]

            st.session_state.temp_recipe = {}
            st.rerun()

# =========================
# TAB 3
# =========================
with tab3:

    st.subheader("Manage recipes")

    recipe_list = list(st.session_state.recipes.keys())

    if not recipe_list:
        st.info("No recipes")
        st.stop()

    recipe_to_edit = st.selectbox("Select recipe", recipe_list)
    recipe = st.session_state.recipes[recipe_to_edit]

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✏️ Edit Recipe"):
            st.session_state.edit_mode = recipe_to_edit

    with col2:
        if st.button("👁 View Mode"):
            st.session_state.edit_mode = None

    with col3:
        if st.button("🗑 Delete Recipe"):
            del st.session_state.recipes[recipe_to_edit]

            st.session_state.data["recipes"] = st.session_state.recipes
            save_data(st.session_state.data)

            # 🔥 reload
            st.session_state.data = load_data()
            st.session_state.recipes = st.session_state.data["recipes"]

            st.session_state.edit_mode = None

            st.success("Recipe deleted")
            st.rerun()

    if st.session_state.edit_mode != recipe_to_edit:

        for ing, d in recipe["ingredients"].items():
            st.write(f"{ing}: {format_qty(d['qty'])} {d['unit']}")

        st.info(recipe.get("instructions", ""))

    else:

        new_instructions = st.text_area(
            "Instructions",
            value=recipe.get("instructions", "")
        )

        if "edit_buffer" not in st.session_state:
            st.session_state.edit_buffer = recipe["ingredients"].copy()

        edited = st.session_state.edit_buffer

        for ing in list(edited.keys()):

            col1, col2, col3 = st.columns(3)

            with col1:
                qty_val = st.number_input(
                    f"{ing} qty",
                    value=float(edited[ing]["qty"]),
                    key=f"qty_{ing}"
                )

            with col2:
                unit_val = st.selectbox(
                    f"{ing} unit",
                    st.session_state.units,
                    index=st.session_state.units.index(
                        edited[ing]["unit"]
                    ) if edited[ing]["unit"] in st.session_state.units else 0,
                    key=f"unit_{ing}"
                )

            with col3:
                if st.button("❌", key=f"del_{ing}"):
                    del st.session_state.edit_buffer[ing]
                    st.rerun()

            edited[ing]["qty"] = qty_val
            edited[ing]["unit"] = unit_val

        new_ing = st.text_input("Add ingredient")
        new_qty = st.number_input("Qty", min_value=0.0)
        new_unit = st.selectbox("Unit", st.session_state.units)

        if st.button("➕ Add Ingredient"):
            if new_ing:
                st.session_state.edit_buffer[new_ing] = {
                    "qty": new_qty,
                    "unit": new_unit
                }
                st.rerun()

        if st.button("💾 Save Changes"):

            st.session_state.recipes[recipe_to_edit] = {
                "ingredients": st.session_state.edit_buffer,
                "instructions": new_instructions
            }

            st.session_state.data["recipes"] = st.session_state.recipes
            save_data(st.session_state.data)

            # 🔥 reload
            st.session_state.data = load_data()
            st.session_state.recipes = st.session_state.data["recipes"]

            del st.session_state.edit_buffer
            st.session_state.edit_mode = None

            st.success("Saved!")
            st.rerun()