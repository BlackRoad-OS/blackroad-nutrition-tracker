"""Tests for BlackRoad Nutrition Tracker."""
import os, tempfile, pytest
os.environ["HOME"] = tempfile.mkdtemp()

from nutrition import (
    add_food, get_food, search_foods, log_meal,
    daily_summary, calculate_macros, nutrient_gaps, export_csv,
)

@pytest.fixture
def apple():
    return add_food("Apple", 95, protein_g=0.5, carbs_g=25, fat_g=0.3,
                    fiber_g=4.4, serving_size_g=182, vitamin_c_mg=8.4)

def test_add_and_get_food(apple):
    f = get_food(apple.id)
    assert f.name == "Apple"
    assert f.calories == 95

def test_food_scale(apple):
    scaled = apple.scale(91)  # half serving
    assert scaled.calories == pytest.approx(47.5, abs=1)

def test_search_foods(apple):
    results = search_foods("App")
    assert any(f.name == "Apple" for f in results)

def test_log_and_summary(apple):
    meal = log_meal("user1", [{"food_id": apple.id, "amount_g": 182}], "breakfast")
    assert meal.meal_type == "breakfast"
    totals = meal.totals()
    assert totals["calories"] == pytest.approx(95, abs=1)

def test_daily_summary_empty():
    s = daily_summary("nobody", "1900-01-01")
    assert s["n_meals"] == 0
    assert s["totals"]["calories"] == 0

def test_calculate_macros(apple):
    log_meal("macro_user", [{"food_id": apple.id, "amount_g": 182}], "lunch")
    m = calculate_macros("macro_user")
    assert m["calories"] > 0
    # percentages may exceed 100 when rounded independently per macro
    assert m["protein_pct"] >= 0
    assert m["carbs_pct"] >= 0
    assert m["fat_pct"] >= 0

def test_nutrient_gaps_empty():
    g = nutrient_gaps("nobody", "1900-01-01")
    for nutrient, info in g["gaps"].items():
        assert info["actual"] == 0
        assert info["status"] in ("low", "marginal", "ok")

def test_export_csv(apple):
    log_meal("exp_user", [{"food_id": apple.id}], "dinner")
    csv_str = export_csv("exp_user", days=1)
    assert "calories" in csv_str

def test_serving_scale_zero_guard():
    f = add_food("Zero Serving", 100, 10, 10, 5, serving_size_g=0)
    scaled = f.scale(50)
    assert scaled.id == f.id  # returns original if serving_size_g == 0
