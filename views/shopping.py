import streamlit as st
from utils import format_qty, generate_shopping_list
from storage import save_data, load_data


def show_shopping_tab():

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
            st.session_state.checked_items = {}
            st.session_state.view = "checklist"
            st.rerun()