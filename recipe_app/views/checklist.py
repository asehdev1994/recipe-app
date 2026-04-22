import streamlit as st
from recipe_app.utils import format_qty


def show_checklist():
    st.title("🛒 Shopping Checklist")

    shopping = st.session_state.get("current_shopping", {})

    if "checked_items" not in st.session_state:
        st.session_state.checked_items = {}

    if not shopping:
        st.warning("No shopping list")

    else:
        # Initialise state
        for k in shopping.keys():
            if k not in st.session_state.checked_items:
                st.session_state.checked_items[k] = False

        # Sort: unchecked first
        sorted_items = sorted(
            shopping.items(),
            key=lambda x: st.session_state.checked_items[x[0]]
        )

        def toggle_item(item_key):
            st.session_state.checked_items[item_key] = not st.session_state.checked_items[item_key]

        for k, v in sorted_items:
            st.checkbox(
                f"{k}: {format_qty(v['qty'])} {v['unit']}",
                value=st.session_state.checked_items[k],
                key=f"check_{k}",
                on_change=toggle_item,
                args=(k,)
            )

    if st.button("⬅ Back"):
        st.session_state.view = "main"
        st.rerun()
