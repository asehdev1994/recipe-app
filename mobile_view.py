import streamlit as st
import json
from storage import load_sessions
from utils import format_qty

# =========================
# MOBILE HTML GENERATOR
# =========================
def generate_mobile_html(shopping, session_id):

    items = [
        {
            "name": k,
            "qty": format_qty(v["qty"]),
            "unit": v["unit"]
        }
        for k, v in shopping.items()
    ]

    return f"""
<!DOCTYPE html>
<html>
head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#ffffff">

<link rel="manifest" href="data:application/json,{{
  &quot;name&quot;:&quot;Shopping List&quot;,
  &quot;short_name&quot;:&quot;Shopping&quot;,
  &quot;display&quot;:&quot;standalone&quot;,
  &quot;background_color&quot;:&quot;#ffffff&quot;,
  &quot;theme_color&quot;:&quot;#ffffff&quot;
}}">

<style>
body {{
    font-family: Arial;
    background: #f5f5f5;
    padding: 10px;
    margin: 0;
}}

h2 {{
    text-align: center;
}}

.item {{
    background: white;
    margin: 8px 0;
    padding: 15px;
    border-radius: 10px;
    font-size: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}}

.checked {{
    text-decoration: line-through;
    opacity: 0.5;
}}
</style>
</head>

<body>

<h2>🛒 Shopping List</h2>
<div id="list"></div>

<script>

const SESSION_ID = "{session_id}";

let items = {json.dumps(items)};

// =========================
// LOAD STATE
// =========================
let saved = localStorage.getItem("shopping_state_" + SESSION_ID);
if (saved) {{
    let state = JSON.parse(saved);
    items.forEach(i => {{
        if (state[i.name] !== undefined) {{
            i.checked = state[i.name];
        }} else {{
            i.checked = false;
        }}
    }});
}} else {{
    items.forEach(i => i.checked = false);
}}

// =========================
// SAVE STATE
// =========================
function saveState() {{
    let state = {{}};
    items.forEach(i => state[i.name] = i.checked);
    localStorage.setItem("shopping_state_" + SESSION_ID, JSON.stringify(state));
}}

// =========================
// RENDER
// =========================
function render() {{

    let container = document.getElementById("list");
    container.innerHTML = "";

    // sort: unchecked first
    items.sort((a,b) => a.checked - b.checked);

    items.forEach((item, index) => {{

        let row = document.createElement("div");
        row.className = "item " + (item.checked ? "checked" : "");

        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = item.checked;

        checkbox.onclick = () => toggle(index);

        let label = document.createElement("span");
        label.innerText = `${{item.name}} - ${{item.qty}} ${{item.unit}}`;

        // make entire row clickable
        row.onclick = () => toggle(index);

        row.appendChild(checkbox);
        row.appendChild(label);

        container.appendChild(row);
    }});
}}

// =========================
// TOGGLE
// =========================
function toggle(i) {{
    items[i].checked = !items[i].checked;
    saveState();
    render();
}}

render();

</script>

</body>
</html>
"""

# =========================
# MOBILE RENDER
# =========================
def render_mobile():

    query_params = st.query_params
    session_id = query_params.get("id")

    sessions = load_sessions()

    if not session_id or session_id not in sessions:
        st.error("Invalid or expired session")
        st.stop()

    shopping = sessions[session_id]

    html = generate_mobile_html(shopping, session_id)

    st.components.v1.html(html, height=1000, scrolling=True)