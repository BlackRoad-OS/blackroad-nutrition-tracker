#!/usr/bin/env python3
"""
BlackRoad Nutrition Tracker
Production nutrition logging with macro calculation, RDA comparison, and CSV export.

Usage:
    python nutrition.py add-food --name "Apple" --cal 95 --protein 0.5 --carbs 25 --fat 0.3
    python nutrition.py log-meal --user alice --meal breakfast --foods 1:150,2:80
    python nutrition.py summary --user alice --date 2024-01-15
    python nutrition.py macros --user alice --date 2024-01-15
    python nutrition.py gaps --user alice --date 2024-01-15
    python nutrition.py export --user alice --days 30
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta, date
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = Path.home() / ".blackroad" / "nutrition_tracker.db"

# ── RDA / DRI reference values ─────────────────────────────────────────────────
RDA: Dict[str, Dict[str, float]] = {
    "calories":    {"male": 2500, "female": 2000, "default": 2000},
    "protein_g":   {"male": 56,   "female": 46,   "default": 50},
    "carbs_g":     {"male": 300,  "female": 225,  "default": 260},
    "fat_g":       {"male": 78,   "female": 65,   "default": 70},
    "fiber_g":     {"male": 38,   "female": 25,   "default": 30},
    "sodium_mg":   {"male": 2300, "female": 2300, "default": 2300},
    "calcium_mg":  {"male": 1000, "female": 1000, "default": 1000},
    "iron_mg":     {"male": 8,    "female": 18,   "default": 12},
    "vitamin_c_mg":{"male": 90,   "female": 75,   "default": 80},
    "vitamin_d_iu":{"male": 600,  "female": 600,  "default": 600},
    "potassium_mg":{"male": 3400, "female": 2600, "default": 3000},
}

MACRO_KEYS    = ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"]
MICRONUTRIENTS = ["sodium_mg", "calcium_mg", "iron_mg", "vitamin_c_mg", "vitamin_d_iu", "potassium_mg"]


# ── Dataclasses ────────────────────────────────────────────────────────────────

@dataclass
class Food:
    id:              int
    name:            str
    calories:        float
    protein_g:       float
    carbs_g:         float
    fat_g:           float
    fiber_g:         float
    serving_size_g:  float
    sodium_mg:       float = 0.0
    calcium_mg:      float = 0.0
    iron_mg:         float = 0.0
    vitamin_c_mg:    float = 0.0
    vitamin_d_iu:    float = 0.0
    potassium_mg:    float = 0.0
    brand:           str   = ""
    category:        str   = "general"
    created_at:      str   = field(default_factory=lambda: datetime.now().isoformat())

    def scale(self, amount_g: float) -> "Food":
        """Return a new Food scaled to the given gram weight."""
        if self.serving_size_g <= 0:
            return self
        factor = amount_g / self.serving_size_g
        return Food(
            id=self.id, name=self.name,
            calories=round(self.calories * factor, 2),
            protein_g=round(self.protein_g * factor, 2),
            carbs_g=round(self.carbs_g * factor, 2),
            fat_g=round(self.fat_g * factor, 2),
            fiber_g=round(self.fiber_g * factor, 2),
            serving_size_g=amount_g,
            sodium_mg=round(self.sodium_mg * factor, 2),
            calcium_mg=round(self.calcium_mg * factor, 2),
            iron_mg=round(self.iron_mg * factor, 2),
            vitamin_c_mg=round(self.vitamin_c_mg * factor, 2),
            vitamin_d_iu=round(self.vitamin_d_iu * factor, 2),
            potassium_mg=round(self.potassium_mg * factor, 2),
            brand=self.brand, category=self.category, created_at=self.created_at,
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Meal:
    id:        int
    user_id:   str
    meal_type: str          # breakfast / lunch / dinner / snack
    date:      str          # YYYY-MM-DD
    logged_at: str
    notes:     str
    items:     List[dict] = field(default_factory=list)

    def totals(self) -> dict:
        out: Dict[str, float] = {k: 0.0 for k in MACRO_KEYS + MICRONUTRIENTS}
        for item in self.items:
            for k in out:
                out[k] = round(out[k] + item.get(k, 0.0), 2)
        return out

    def to_dict(self) -> dict:
        d = asdict(self)
        d["totals"] = self.totals()
        return d


@dataclass
class FoodLog:
    user_id: str
    meals:   List[Meal]

    def daily_totals(self, log_date: str) -> dict:
        totals: Dict[str, float] = {k: 0.0 for k in MACRO_KEYS + MICRONUTRIENTS}
        for meal in self.meals:
            if meal.date == log_date:
                for k, v in meal.totals().items():
                    totals[k] = round(totals[k] + v, 2)
        return totals


# ── Database ───────────────────────────────────────────────────────────────────

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS foods (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT    NOT NULL,
            calories       REAL    NOT NULL DEFAULT 0,
            protein_g      REAL    NOT NULL DEFAULT 0,
            carbs_g        REAL    NOT NULL DEFAULT 0,
            fat_g          REAL    NOT NULL DEFAULT 0,
            fiber_g        REAL    NOT NULL DEFAULT 0,
            serving_size_g REAL    NOT NULL DEFAULT 100,
            sodium_mg      REAL    NOT NULL DEFAULT 0,
            calcium_mg     REAL    NOT NULL DEFAULT 0,
            iron_mg        REAL    NOT NULL DEFAULT 0,
            vitamin_c_mg   REAL    NOT NULL DEFAULT 0,
            vitamin_d_iu   REAL    NOT NULL DEFAULT 0,
            potassium_mg   REAL    NOT NULL DEFAULT 0,
            brand          TEXT    NOT NULL DEFAULT '',
            category       TEXT    NOT NULL DEFAULT 'general',
            created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_food_name ON foods(name);

        CREATE TABLE IF NOT EXISTS meals (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            date      TEXT NOT NULL,
            logged_at TEXT NOT NULL DEFAULT (datetime('now')),
            notes     TEXT NOT NULL DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_meal_user_date ON meals(user_id, date);

        CREATE TABLE IF NOT EXISTS meal_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id      INTEGER NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
            food_id      INTEGER NOT NULL REFERENCES foods(id),
            food_name    TEXT    NOT NULL DEFAULT '',
            amount_g     REAL    NOT NULL DEFAULT 100,
            calories     REAL    NOT NULL DEFAULT 0,
            protein_g    REAL    NOT NULL DEFAULT 0,
            carbs_g      REAL    NOT NULL DEFAULT 0,
            fat_g        REAL    NOT NULL DEFAULT 0,
            fiber_g      REAL    NOT NULL DEFAULT 0,
            sodium_mg    REAL    NOT NULL DEFAULT 0,
            calcium_mg   REAL    NOT NULL DEFAULT 0,
            iron_mg      REAL    NOT NULL DEFAULT 0,
            vitamin_c_mg REAL    NOT NULL DEFAULT 0,
            vitamin_d_iu REAL    NOT NULL DEFAULT 0,
            potassium_mg REAL    NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS user_prefs (
            user_id        TEXT PRIMARY KEY,
            sex            TEXT NOT NULL DEFAULT 'default',
            age            INTEGER NOT NULL DEFAULT 0,
            weight_kg      REAL    NOT NULL DEFAULT 0,
            height_cm      REAL    NOT NULL DEFAULT 0,
            activity_level TEXT    NOT NULL DEFAULT 'moderate'
        );
    """)
    conn.commit()


# ── Food API ───────────────────────────────────────────────────────────────────

def add_food(
    name: str, calories: float, protein_g: float, carbs_g: float,
    fat_g: float, fiber_g: float = 0.0, serving_size_g: float = 100.0,
    **extras
) -> Food:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO foods(name,calories,protein_g,carbs_g,fat_g,fiber_g,serving_size_g,"
            "sodium_mg,calcium_mg,iron_mg,vitamin_c_mg,vitamin_d_iu,potassium_mg,brand,category)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (name, calories, protein_g, carbs_g, fat_g, fiber_g, serving_size_g,
             extras.get("sodium_mg", 0), extras.get("calcium_mg", 0),
             extras.get("iron_mg", 0), extras.get("vitamin_c_mg", 0),
             extras.get("vitamin_d_iu", 0), extras.get("potassium_mg", 0),
             extras.get("brand", ""), extras.get("category", "general")),
        )
        conn.commit()
        return get_food(cur.lastrowid)


def get_food(food_id: int) -> Optional[Food]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM foods WHERE id=?", (food_id,)).fetchone()
    return Food(**dict(row)) if row else None


def search_foods(query: str, limit: int = 20) -> List[Food]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM foods WHERE name LIKE ? ORDER BY name LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
    return [Food(**dict(r)) for r in rows]


# ── Meal API ───────────────────────────────────────────────────────────────────

def log_meal(
    user_id: str,
    foods: List[Dict],
    meal_type: str = "lunch",
    log_date: Optional[str] = None,
    notes: str = "",
) -> Meal:
    if log_date is None:
        log_date = date.today().isoformat()
    now = datetime.now().isoformat()

    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO meals(user_id,meal_type,date,logged_at,notes) VALUES(?,?,?,?,?)",
            (user_id, meal_type, log_date, now, notes),
        )
        meal_id = cur.lastrowid

        items_data = []
        for entry in foods:
            fid    = entry["food_id"]
            amount = entry.get("amount_g", 100.0)
            food   = get_food(fid)
            if not food:
                continue
            scaled = food.scale(amount)
            conn.execute(
                "INSERT INTO meal_items(meal_id,food_id,food_name,amount_g,"
                "calories,protein_g,carbs_g,fat_g,fiber_g,"
                "sodium_mg,calcium_mg,iron_mg,vitamin_c_mg,vitamin_d_iu,potassium_mg)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (meal_id, fid, food.name, amount,
                 scaled.calories, scaled.protein_g, scaled.carbs_g,
                 scaled.fat_g, scaled.fiber_g,
                 scaled.sodium_mg, scaled.calcium_mg, scaled.iron_mg,
                 scaled.vitamin_c_mg, scaled.vitamin_d_iu, scaled.potassium_mg),
            )
            items_data.append({
                "food_id": fid, "food_name": food.name, "amount_g": amount,
                "calories": scaled.calories, "protein_g": scaled.protein_g,
                "carbs_g": scaled.carbs_g, "fat_g": scaled.fat_g, "fiber_g": scaled.fiber_g,
                "sodium_mg": scaled.sodium_mg, "calcium_mg": scaled.calcium_mg,
                "iron_mg": scaled.iron_mg, "vitamin_c_mg": scaled.vitamin_c_mg,
                "vitamin_d_iu": scaled.vitamin_d_iu, "potassium_mg": scaled.potassium_mg,
            })
        conn.commit()

    return Meal(meal_id, user_id, meal_type, log_date, now, notes, items_data)


def _get_meals(user_id: str, log_date: str) -> List[Meal]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM meals WHERE user_id=? AND date=? ORDER BY logged_at",
            (user_id, log_date),
        ).fetchall()
        meals = []
        for row in rows:
            m = dict(row)
            item_rows = conn.execute(
                "SELECT * FROM meal_items WHERE meal_id=?", (m["id"],)
            ).fetchall()
            m["items"] = [dict(r) for r in item_rows]
            meals.append(Meal(**m))
    return meals


def daily_summary(user_id: str, log_date: Optional[str] = None) -> dict:
    if log_date is None:
        log_date = date.today().isoformat()
    meals   = _get_meals(user_id, log_date)
    fl      = FoodLog(user_id, meals)
    totals  = fl.daily_totals(log_date)
    return {
        "user_id": user_id,
        "date":    log_date,
        "n_meals": len(meals),
        "meals":   [m.to_dict() for m in meals],
        "totals":  totals,
    }


def calculate_macros(user_id: str, log_date: Optional[str] = None) -> dict:
    if log_date is None:
        log_date = date.today().isoformat()
    summary = daily_summary(user_id, log_date)
    totals  = summary["totals"]
    cal     = totals.get("calories", 0) or 1
    return {
        "user_id":    user_id,
        "date":       log_date,
        "calories":   totals["calories"],
        "protein_g":  totals["protein_g"],
        "carbs_g":    totals["carbs_g"],
        "fat_g":      totals["fat_g"],
        "fiber_g":    totals["fiber_g"],
        "protein_pct": round(totals["protein_g"] * 4 / cal * 100, 1),
        "carbs_pct":   round(totals["carbs_g"]   * 4 / cal * 100, 1),
        "fat_pct":     round(totals["fat_g"]     * 9 / cal * 100, 1),
    }


def nutrient_gaps(user_id: str, log_date: Optional[str] = None, sex: str = "default") -> dict:
    if log_date is None:
        log_date = date.today().isoformat()
    summary = daily_summary(user_id, log_date)
    totals  = summary["totals"]
    gaps: Dict[str, dict] = {}
    for nutrient, ref in RDA.items():
        target  = ref.get(sex, ref["default"])
        actual  = totals.get(nutrient, 0.0)
        pct     = round(actual / target * 100, 1) if target else 0
        deficit = round(target - actual, 2)
        gaps[nutrient] = {
            "actual":  actual,
            "target":  target,
            "pct_met": pct,
            "deficit": deficit if deficit > 0 else 0,
            "surplus": abs(deficit) if deficit < 0 else 0,
            "status":  "ok" if pct >= 80 else "low" if pct < 50 else "marginal",
        }
    return {"user_id": user_id, "date": log_date, "gaps": gaps}


def export_csv(user_id: str, days: int = 30) -> str:
    all_dates = [
        (date.today() - timedelta(days=i)).isoformat() for i in range(days)
    ]
    out    = StringIO()
    writer = csv.writer(out)
    writer.writerow(["date"] + MACRO_KEYS + MICRONUTRIENTS)
    for d in sorted(all_dates):
        meals = _get_meals(user_id, d)
        if not meals:
            continue
        fl     = FoodLog(user_id, meals)
        totals = fl.daily_totals(d)
        writer.writerow([d] + [totals.get(k, 0.0) for k in MACRO_KEYS + MICRONUTRIENTS])
    return out.getvalue()


# ── CLI ────────────────────────────────────────────────────────────────────────

def _print(obj):
    print(json.dumps(obj if not isinstance(obj, str) else {"output": obj}, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(description="BlackRoad Nutrition Tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add-food", help="Add a food to the database")
    p.add_argument("--name",     required=True)
    p.add_argument("--cal",      type=float, required=True, dest="calories")
    p.add_argument("--protein",  type=float, default=0,   dest="protein_g")
    p.add_argument("--carbs",    type=float, default=0,   dest="carbs_g")
    p.add_argument("--fat",      type=float, default=0,   dest="fat_g")
    p.add_argument("--fiber",    type=float, default=0,   dest="fiber_g")
    p.add_argument("--serving",  type=float, default=100, dest="serving_size_g")
    p.add_argument("--sodium",   type=float, default=0,   dest="sodium_mg")
    p.add_argument("--calcium",  type=float, default=0,   dest="calcium_mg")
    p.add_argument("--iron",     type=float, default=0,   dest="iron_mg")
    p.add_argument("--vitc",     type=float, default=0,   dest="vitamin_c_mg")
    p.add_argument("--vitd",     type=float, default=0,   dest="vitamin_d_iu")
    p.add_argument("--potassium",type=float, default=0,   dest="potassium_mg")
    p.add_argument("--brand",    default="")
    p.add_argument("--category", default="general")

    p = sub.add_parser("search", help="Search foods by name")
    p.add_argument("query")

    p = sub.add_parser("log-meal", help="Log a meal")
    p.add_argument("--user",  required=True)
    p.add_argument("--meal",  required=True, choices=["breakfast","lunch","dinner","snack"],
                   dest="meal_type")
    p.add_argument("--foods", required=True, help="food_id[:amount_g],... e.g. 1:150,2:80")
    p.add_argument("--date",  default=None)
    p.add_argument("--notes", default="")

    p = sub.add_parser("summary", help="Daily meal summary")
    p.add_argument("--user", required=True)
    p.add_argument("--date", default=None)

    p = sub.add_parser("macros", help="Daily macro breakdown")
    p.add_argument("--user", required=True)
    p.add_argument("--date", default=None)

    p = sub.add_parser("gaps", help="Nutrient gaps vs RDA")
    p.add_argument("--user", required=True)
    p.add_argument("--date", default=None)
    p.add_argument("--sex",  default="default", choices=["male","female","default"])

    p = sub.add_parser("export", help="Export daily totals as CSV")
    p.add_argument("--user", required=True)
    p.add_argument("--days", type=int, default=30)

    args = parser.parse_args()

    if args.cmd == "add-food":
        f = add_food(
            args.name, args.calories, args.protein_g, args.carbs_g, args.fat_g,
            args.fiber_g, args.serving_size_g,
            sodium_mg=args.sodium_mg, calcium_mg=args.calcium_mg, iron_mg=args.iron_mg,
            vitamin_c_mg=args.vitamin_c_mg, vitamin_d_iu=args.vitamin_d_iu,
            potassium_mg=args.potassium_mg, brand=args.brand, category=args.category,
        )
        _print({"status": "added", "id": f.id, "name": f.name, "calories": f.calories})

    elif args.cmd == "search":
        foods = search_foods(args.query)
        _print([f.to_dict() for f in foods])

    elif args.cmd == "log-meal":
        food_entries = []
        for token in args.foods.split(","):
            parts = token.strip().split(":")
            food_entries.append({
                "food_id":  int(parts[0]),
                "amount_g": float(parts[1]) if len(parts) > 1 else 100.0,
            })
        meal = log_meal(args.user, food_entries, args.meal_type, args.date, args.notes)
        _print(meal.to_dict())

    elif args.cmd == "summary":
        _print(daily_summary(args.user, args.date))

    elif args.cmd == "macros":
        _print(calculate_macros(args.user, args.date))

    elif args.cmd == "gaps":
        _print(nutrient_gaps(args.user, args.date, args.sex))

    elif args.cmd == "export":
        print(export_csv(args.user, args.days))


if __name__ == "__main__":
    main()
