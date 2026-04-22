import streamlit as st
from recipe_app.services.storage import load_data, save_data


def show_add_recipe_tab():

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
