from recipe_app.utils import format_qty, generate_shopping_list


def test_format_qty_strips_trailing_decimal_for_whole_numbers():
    assert format_qty(2.0) == "2"


def test_format_qty_rounds_fractional_values():
    assert format_qty(2.345) == "2.35"


def test_generate_shopping_list_aggregates_scaled_ingredients():
    recipes = {
        "Pasta": {
            "ingredients": {
                "Tomato": {"qty": 2, "unit": "pcs"},
                "Basil": {"qty": 0.5, "unit": "cup"},
            }
        },
        "Salad": {
            "ingredients": {
                "Tomato": {"qty": 1, "unit": "pcs"},
                "Oil": {"qty": 2, "unit": "tbsp"},
            }
        },
    }

    result = generate_shopping_list(
        selected_recipes=["Pasta", "Salad"],
        recipes=recipes,
        recipe_scales={"Pasta": 2},
    )

    assert result == {
        "Tomato": {"qty": 5, "unit": "pcs"},
        "Basil": {"qty": 1.0, "unit": "cup"},
        "Oil": {"qty": 2, "unit": "tbsp"},
    }
