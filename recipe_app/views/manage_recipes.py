import streamlit as st
from recipe_app.services.storage import load_data, save_data
from recipe_app.utils import format_qty


def show_manage_recipes_tab():

    st.subheader("Manage recipes")

    recipe_list = list(st.session_state.recipes.keys())

    if not recipe_list:
        st.info("No recipes")
        return

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
