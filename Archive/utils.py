import qrcode
from io import BytesIO

# =========================
# FORMAT QTY
# =========================
def format_qty(qty):
    return str(int(qty)) if float(qty).is_integer() else str(round(qty, 2))


# =========================
# SHOPPING LIST LOGIC
# =========================
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


# =========================
# QR GENERATION
# =========================
def generate_qr(data_str):
    qr = qrcode.make(data_str)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf