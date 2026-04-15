import streamlit as st
import json
import qrcode
import uuid
from io import BytesIO

# =========================
# GLOBAL STORE (SHARED)
# =========================
if "GLOBAL_SHOPPING_SESSIONS" not in globals():
    GLOBAL_SHOPPING_SESSIONS = {}

query_params = st.query_params

# =========================
# LOAD / SAVE
# =========================
def load_data():
    try:
        with open("recipes.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "units": ["g", "kg", "ml", "l", "tsp", "tbsp", "cup", "pcs"],
            "recipes": {}
        }

def save_data(data):
    with open("recipes.json", "w") as f:
        json.dump(data, f, indent=4)

# =========================
# HELPERS
# =========================

SESSION_FILE = "shopping_sessions.json"

def load_sessions():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def format_qty(qty):
    return str(int(qty)) if float(qty).is_integer() else str(round(qty, 2))


def generate_shopping_list(selected_recipes, recipes, recipe_scales):
    items = {}

    for recipe in selected_recipes:
        scale = recipe_scales.get(recipe, 1)

        for ing, details in recipes[recipe]["ingredients"].items():

            if ing not in items:
                items[ing] = {
                    "qty": 0,
                    "unit": details["unit"],
                }

            items[ing]["qty"] += details["qty"] * scale

    return items


def generate_qr(data_str):
    qr = qrcode.make(data_str)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf


# =========================
# INIT STATE
# =========================
if "data" not in st.session_state:
    st.session_state.data = load_data()

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
# UI
# =========================

# =========================
# MOBILE MODE
# =========================
if query_params.get("mobile") == "1":

    session_id = query_params.get("id")
	
    sessions = load_sessions()
    if not session_id or session_id not in sessions:
        st.error("Invalid or expired session")
        st.stop()

    shopping = sessions[session_id]

    st.markdown("## 🛒 Shopping List")

    # Convert to list for ordering
    if "mobile_items" not in st.session_state:
        st.session_state.mobile_items = [
            {"name": k, "qty": v["qty"], "unit": v["unit"], "checked": False}
            for k, v in shopping.items()
        ]

    items = st.session_state.mobile_items

    updated = []

    # ✅ FIXED LOOP (stable keys + inline layout)
    for item in items:

        key = f"m_{item['name']}"  # stable key

        checked = st.checkbox(
            f"{item['name']} - {format_qty(item['qty'])} {item['unit']}",
            value=item["checked"],
            key=key
        )

        item["checked"] = checked
        updated.append(item)

    # Auto sort AFTER processing
    st.session_state.mobile_items = sorted(updated, key=lambda x: x["checked"])

    st.stop()

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

        shopping = generate_shopping_list(
            selected,
            st.session_state.recipes,
            st.session_state.recipe_scales
        )

        st.subheader("Shopping List")

        for k, v in shopping.items():
            st.write(f"{k}: {format_qty(v['qty'])} {v['unit']}")

        # ✅ FIXED QR GENERATION
        if st.button("📱 Generate Mobile Checklist"):

            session_id = str(uuid.uuid4())
            sessions = load_sessions()
            sessions[session_id] = shopping
            save_sessions(sessions)

            BASE_URL = "http://192.168.1.221:8501"
            url = f"{BASE_URL}/?mobile=1&id={session_id}"
	    
            qr = generate_qr(url)

            st.success("Scan this on your phone")
            st.image(qr, use_container_width=True)
            st.code(url)

# =========================
# TAB 2 (UNCHANGED)
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

            st.session_state.temp_recipe = {}
            st.rerun()

# =========================
# TAB 3 (UNCHANGED)
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

            st.session_state.edit_mode = None

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

            del st.session_state.edit_buffer
            st.session_state.edit_mode = None

            st.success("Saved!")
            st.rerun()