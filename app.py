import streamlit as st
from storage import load_data, save_data, delete_user
from utils import format_qty, generate_shopping_list
from auth import sign_in, sign_up
from auth_ui import show_auth
from views.checklist import show_checklist

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

# =========================
# TAB 1 — SHOPPING
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
        if extra_name:
            st.session_state.extra_items[extra_name] = {
                "qty": extra_qty,
                "unit": extra_unit
            }
            st.rerun()

    if st.session_state.extra_items:
        for k, v in st.session_state.extra_items.items():
            st.write(f"{k}: {format_qty(v['qty'])} {v['unit']}")

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

        if st.button("📱 Open Checklist"):
            st.session_state.current_shopping = shopping
            st.session_state.checked_items = {}  # reset state
            st.session_state.view = "checklist"
            st.rerun()

# =========================
# TAB 2 — ADD RECIPE
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
        if "new_unit_input" not in st.session_state:
            st.session_state.new_unit_input = ""

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

                st.session_state.data = load_data()
                st.session_state.units = st.session_state.data["units"]

                st.session_state.new_unit_input = ""
                st.success("Unit added")
                st.rerun()
    else:
        unit = unit_choice

    if st.button("Add ingredient"):
        if ingredient_name:
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

            st.session_state.temp_recipe = {}
            st.rerun()

# =========================
# TAB 3 — MANAGE RECIPES
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
            st.success("Recipe deleted")
            st.rerun()

    # =========================
    # VIEW MODE
    # =========================
    if st.session_state.edit_mode != recipe_to_edit:

        for ing, d in recipe["ingredients"].items():
            st.write(f"{ing}: {format_qty(d['qty'])} {d['unit']}")

        st.info(recipe.get("instructions", ""))

    # =========================
    # EDIT MODE
    # =========================
    else:

        new_instructions = st.text_area(
            "Instructions",
            value=recipe.get("instructions", "")
        )

        if "edit_buffer" not in st.session_state:
            st.session_state.edit_buffer = recipe["ingredients"].copy()

        edited = st.session_state.edit_buffer

        # 🔁 EDIT EXISTING INGREDIENTS
        for ing in list(edited.keys()):

            col1, col2, col3 = st.columns(3)

            with col1:
                qty_val = st.number_input(
                    f"{ing} qty",
                    value=float(edited[ing]["qty"]),
                    key=f"qty_{ing}"
                )

            with col2:
                unit_choice = st.selectbox(
                    f"{ing} unit",
                    st.session_state.units + ["➕ Add new unit"],
                    index=st.session_state.units.index(
                        edited[ing]["unit"]
                    ) if edited[ing]["unit"] in st.session_state.units else 0,
                    key=f"unit_{ing}"
                )

                unit_val = None

                if unit_choice == "➕ Add new unit":
                    new_unit_input = st.text_input(
                        f"New unit for {ing}",
                        key=f"new_unit_{ing}"
                    )

                    if st.button(f"Add unit {ing}"):
                        new_unit = new_unit_input.strip().lower()

                        if new_unit and new_unit not in st.session_state.units:
                            st.session_state.units.append(new_unit)
                            st.session_state.data["units"] = st.session_state.units
                            save_data(st.session_state.data)

                            st.session_state.data = load_data()
                            st.session_state.units = st.session_state.data["units"]

                            st.success(f"Added unit: {new_unit}")
                            st.rerun()
                else:
                    unit_val = unit_choice

            with col3:
                if st.button("❌", key=f"del_{ing}"):
                    del st.session_state.edit_buffer[ing]
                    st.rerun()

            if unit_val:
                edited[ing]["qty"] = qty_val
                edited[ing]["unit"] = unit_val

        # ➕ ADD NEW INGREDIENT
        st.markdown("### ➕ Add Ingredient")

        new_ing = st.text_input("Ingredient name")
        new_qty = st.number_input("Qty", min_value=0.0)

        new_unit_choice = st.selectbox(
            "Unit",
            st.session_state.units + ["➕ Add new unit"],
            key="new_ing_unit"
        )

        new_unit = None

        if new_unit_choice == "➕ Add new unit":
            new_unit_input = st.text_input("New unit", key="new_ing_unit_input")

            if st.button("Add unit (new ingredient)"):
                unit_val = new_unit_input.strip().lower()

                if unit_val and unit_val not in st.session_state.units:
                    st.session_state.units.append(unit_val)
                    st.session_state.data["units"] = st.session_state.units
                    save_data(st.session_state.data)

                    st.session_state.data = load_data()
                    st.session_state.units = st.session_state.data["units"]

                    st.success(f"Added unit: {unit_val}")
                    st.rerun()
        else:
            new_unit = new_unit_choice

        if st.button("➕ Add Ingredient"):
            if new_ing and new_unit:
                st.session_state.edit_buffer[new_ing] = {
                    "qty": new_qty,
                    "unit": new_unit
                }
                st.rerun()

        # 💾 SAVE
        if st.button("💾 Save Changes"):

            st.session_state.recipes[recipe_to_edit] = {
                "ingredients": st.session_state.edit_buffer,
                "instructions": new_instructions
            }

            st.session_state.data["recipes"] = st.session_state.recipes
            save_data(st.session_state.data)

            st.session_state.data = load_data()
            st.session_state.recipes = st.session_state.data["recipes"]

            del st.session_state.edit_buffer
            st.session_state.edit_mode = None

            st.success("Saved!")
            st.rerun()