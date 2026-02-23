# BlackRoad Nutrition Tracker

[![CI](https://github.com/BlackRoad-OS/blackroad-nutrition-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/BlackRoad-OS/blackroad-nutrition-tracker/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)
[![BlackRoad OS](https://img.shields.io/badge/BlackRoad-OS-black.svg)](https://blackroad.io)

> Nutrition logging with macro calculation, RDA comparison, and CSV export

Part of the **BlackRoad OS** health & science platform — production-grade implementations with SQLite persistence, pytest coverage, and CI/CD.

## Features

- **Food** dataclass with full macro/micro nutrient profile (calories, protein, carbs, fat, fiber, vitamins, minerals)
- **Meal** and **FoodLog** aggregation with proportional serving scaling
- `add_food(name, calories, ...)` — add to food database with 14 nutrient fields
- `log_meal(user_id, foods, meal_type)` — breakfast/lunch/dinner/snack logging
- `daily_summary(user_id, date)` — full meal breakdown per day
- `calculate_macros(user_id, date)` — protein/carbs/fat percentages
- `nutrient_gaps(user_id, date)` — compare actual intake vs RDA (11 nutrients)
- `export_csv(user_id, days=30)` — multi-day CSV export

## Quick Start

```bash
python src/nutrition.py add-food --name "Apple" --cal 95 --protein 0.5 --carbs 25 --fat 0.3 --fiber 4.4 --vitc 8.4 --serving 182
python src/nutrition.py log-meal --user alice --meal breakfast --foods 1:182
python src/nutrition.py summary --user alice
python src/nutrition.py macros --user alice
python src/nutrition.py gaps --user alice --sex female
python src/nutrition.py export --user alice --days 7
```

## RDA Nutrients Tracked

Calories, protein, carbohydrates, fat, fiber, sodium, calcium, iron, vitamin C, vitamin D, potassium.

## Installation

```bash
# No dependencies required — pure Python stdlib + sqlite3
python src/nutrition.py --help
```

## Testing

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=src
```

## Data Storage

All data is stored locally in `~/.blackroad/nutrition-tracker.db` (SQLite). Zero external dependencies.

## License

Proprietary — © BlackRoad OS, Inc. All rights reserved.
