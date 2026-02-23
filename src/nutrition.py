#!/usr/bin/env python3
"""
Nutrition tracking and meal planning system.
Personal nutrition management with meal logging and dietary analysis.
"""

import os
import json
import sqlite3
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import uuid
import argparse

# Database setup
DB_PATH = os.path.expanduser("~/.blackroad/nutrition.db")

class FoodCategory(Enum):
    FRUIT = "fruit"
    VEGETABLE = "vegetable"
    GRAIN = "grain"
    PROTEIN = "protein"
    DAIRY = "dairy"
    FAT = "fat"
    BEVERAGE = "beverage"
    SNACK = "snack"

class MealType(Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

@dataclass
class Food:
    id: str
    name: str
    category: str
    calories_per_100g: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float = 0
    sugar_g: float = 0
    sodium_mg: float = 0
    vitamins: Dict = field(default_factory=dict)

@dataclass
class MealEntry:
    id: str
    user_id: str
    food_id: str
    grams: float
    meal_type: str
    date: str
    notes: str = ""

class NutritionTracker:
    def __init__(self):
        self.db_path = DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self._initialize_common_foods()
    
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS foods (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            calories_per_100g REAL NOT NULL,
            protein_g REAL NOT NULL,
            carbs_g REAL NOT NULL,
            fat_g REAL NOT NULL,
            fiber_g REAL DEFAULT 0,
            sugar_g REAL DEFAULT 0,
            sodium_mg REAL DEFAULT 0,
            vitamins TEXT DEFAULT '{}'
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS meals (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            food_id TEXT NOT NULL,
            grams REAL NOT NULL,
            meal_type TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            logged_at TEXT NOT NULL,
            FOREIGN KEY(food_id) REFERENCES foods(id)
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS goals (
            user_id TEXT PRIMARY KEY,
            calories INTEGER DEFAULT 2000,
            protein_g REAL DEFAULT 50,
            carbs_g REAL DEFAULT 260,
            fat_g REAL DEFAULT 65,
            fiber_g REAL DEFAULT 25,
            updated_at TEXT NOT NULL
        )''')
        
        conn.commit()
        conn.close()
    
    def _initialize_common_foods(self):
        """Initialize common foods."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM foods')
        if c.fetchone()[0] == 0:
            common_foods = [
                ('apple', 'fruit', 52, 0.3, 14, 0.2, 2.4, 10),
                ('banana', 'fruit', 89, 1.1, 23, 0.3, 2.6, 12),
                ('chicken_breast', 'protein', 165, 31, 0, 3.6, 0, 0),
                ('rice', 'grain', 130, 2.7, 28, 0.3, 0.4, 0.1),
                ('broccoli', 'vegetable', 34, 2.8, 7, 0.4, 2.4, 1.5),
                ('eggs', 'protein', 155, 13, 1.1, 11, 0, 0.6),
                ('oats', 'grain', 389, 17, 66, 7, 10.6, 0),
                ('salmon', 'protein', 208, 20, 0, 13, 0, 0),
                ('almonds', 'fat', 579, 21, 22, 50, 12.5, 4.4),
                ('spinach', 'vegetable', 23, 2.9, 3.6, 0.4, 2.2, 0.4),
                ('sweet_potato', 'vegetable', 86, 1.6, 20, 0.1, 3, 4.2),
                ('greek_yogurt', 'dairy', 59, 10, 3.3, 0.4, 0, 0.4),
                ('olive_oil', 'fat', 884, 0, 0, 100, 0, 0),
                ('lentils', 'protein', 116, 9, 20, 0.4, 7.8, 1.5),
                ('blueberries', 'fruit', 57, 0.7, 14, 0.3, 2.4, 10),
                ('milk', 'dairy', 61, 3.2, 4.8, 3.3, 0, 0),
                ('cheese', 'dairy', 402, 25, 1.3, 33, 0, 0.7),
                ('bread', 'grain', 265, 9, 49, 3.3, 2.7, 4),
                ('pasta', 'grain', 131, 5, 25, 1.1, 1.8, 0.3),
                ('orange', 'fruit', 47, 0.9, 12, 0.3, 2.4, 9),
            ]
            
            for name, cat, cal, prot, carbs, fat, fiber, sugar in common_foods:
                food_id = f"F_{uuid.uuid4().hex[:8].upper()}"
                c.execute('''INSERT INTO foods VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (food_id, name, cat, cal, prot, carbs, fat, fiber, sugar, 0, '{}'))
            
            conn.commit()
        
        conn.close()
    
    def add_food(self, name: str, category: str, cal: float, protein: float, carbs: float,
                fat: float, fiber: float = 0, sugar: float = 0, sodium: float = 0,
                vitamins: Optional[Dict] = None) -> Food:
        """Add a new food to database."""
        if category not in [c.value for c in FoodCategory]:
            raise ValueError(f"Invalid category. Must be one of {[c.value for c in FoodCategory]}")
        
        food_id = f"F_{uuid.uuid4().hex[:8].upper()}"
        vitamins = vitamins or {}
        
        food = Food(
            id=food_id,
            name=name,
            category=category,
            calories_per_100g=cal,
            protein_g=protein,
            carbs_g=carbs,
            fat_g=fat,
            fiber_g=fiber,
            sugar_g=sugar,
            sodium_mg=sodium,
            vitamins=vitamins
        )
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO foods VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (food.id, food.name, food.category, food.calories_per_100g,
                  food.protein_g, food.carbs_g, food.fat_g, food.fiber_g,
                  food.sugar_g, food.sodium_mg, json.dumps(food.vitamins)))
        conn.commit()
        conn.close()
        
        return food
    
    def log_meal(self, user_id: str, food_id: str, grams: float, meal_type: str,
                date: Optional[str] = None) -> MealEntry:
        """Log a meal entry."""
        if meal_type not in [m.value for m in MealType]:
            raise ValueError(f"Invalid meal type. Must be one of {[m.value for m in MealType]}")
        
        date = date or datetime.now().strftime('%Y-%m-%d')
        meal_id = f"M_{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Verify food exists
        c.execute('SELECT * FROM foods WHERE id = ?', (food_id,))
        if not c.fetchone():
            conn.close()
            raise ValueError(f"Food {food_id} not found")
        
        meal = MealEntry(
            id=meal_id,
            user_id=user_id,
            food_id=food_id,
            grams=grams,
            meal_type=meal_type,
            date=date
        )
        
        c.execute('''INSERT INTO meals VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (meal.id, meal.user_id, meal.food_id, meal.grams,
                  meal.meal_type, meal.date, meal.notes, now))
        
        # Initialize user goals if not exists
        c.execute('SELECT * FROM goals WHERE user_id = ?', (user_id,))
        if not c.fetchone():
            c.execute('''INSERT INTO goals (user_id, updated_at) VALUES (?, ?)''',
                     (user_id, now))
        
        conn.commit()
        conn.close()
        
        return meal
    
    def set_goals(self, user_id: str, calories: int = 2000, protein: float = 50,
                 carbs: float = 260, fat: float = 65, fiber: float = 25):
        """Set daily nutrition goals."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        c.execute('''INSERT OR REPLACE INTO goals (user_id, calories, protein_g, carbs_g, fat_g, fiber_g, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (user_id, calories, protein, carbs, fat, fiber, now))
        conn.commit()
        conn.close()
    
    def get_daily_summary(self, user_id: str, date: Optional[str] = None) -> Dict:
        """Get daily nutrition summary."""
        date = date or datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get meals for the day
        c.execute('''SELECT m.grams, f.calories_per_100g, f.protein_g, f.carbs_g, f.fat_g, f.fiber_g, f.sodium_mg
                    FROM meals m
                    JOIN foods f ON m.food_id = f.id
                    WHERE m.user_id = ? AND m.date = ?''',
                 (user_id, date))
        
        meals = c.fetchall()
        
        # Sum up macros
        totals = {
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0,
            "fiber_g": 0,
            "sodium_mg": 0
        }
        
        for grams, cal, prot, carb, fat, fib, sod in meals:
            multiplier = grams / 100
            totals["calories"] += cal * multiplier
            totals["protein_g"] += prot * multiplier
            totals["carbs_g"] += carb * multiplier
            totals["fat_g"] += fat * multiplier
            totals["fiber_g"] += fib * multiplier
            totals["sodium_mg"] += sod * multiplier
        
        # Get goals
        c.execute('SELECT * FROM goals WHERE user_id = ?', (user_id,))
        goals_row = c.fetchone()
        conn.close()
        
        if goals_row:
            goals = {
                "calories": goals_row[1],
                "protein_g": goals_row[2],
                "carbs_g": goals_row[3],
                "fat_g": goals_row[4],
                "fiber_g": goals_row[5]
            }
        else:
            goals = {
                "calories": 2000,
                "protein_g": 50,
                "carbs_g": 260,
                "fat_g": 65,
                "fiber_g": 25
            }
        
        # Calculate percentages
        summary = {
            "date": date,
            "totals": {k: round(v, 1) for k, v in totals.items()},
            "goals": goals,
            "percentages": {
                "calories": round(totals["calories"] / goals["calories"] * 100, 1),
                "protein": round(totals["protein_g"] / goals["protein_g"] * 100, 1),
                "carbs": round(totals["carbs_g"] / goals["carbs_g"] * 100, 1),
                "fat": round(totals["fat_g"] / goals["fat_g"] * 100, 1)
            },
            "meal_count": len(meals)
        }
        
        return summary
    
    def get_weekly_report(self, user_id: str) -> Dict:
        """Get 7-day nutrition report."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        daily_summaries = []
        total_days = {}
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            summary = self.get_daily_summary(user_id, date)
            daily_summaries.append(summary)
            
            for key, val in summary["totals"].items():
                total_days.setdefault(key, []).append(val)
        
        # Calculate averages
        averages = {k: round(sum(v) / len(v), 1) for k, v in total_days.items()}
        
        conn.close()
        
        return {
            "period": "last_7_days",
            "daily_summaries": daily_summaries,
            "averages": averages
        }
    
    def search_food(self, query: str) -> List[Food]:
        """Search foods by name or category."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query_lower = query.lower()
        c.execute('''SELECT * FROM foods WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ?''',
                 (f'%{query_lower}%', f'%{query_lower}%'))
        
        foods = []
        for row in c.fetchall():
            foods.append(Food(
                id=row[0], name=row[1], category=row[2], calories_per_100g=row[3],
                protein_g=row[4], carbs_g=row[5], fat_g=row[6], fiber_g=row[7],
                sugar_g=row[8], sodium_mg=row[9], vitamins=json.loads(row[10])
            ))
        
        conn.close()
        return foods
    
    def meal_suggestions(self, user_id: str, meal_type: str) -> List[Dict]:
        """Suggest foods to meet remaining macro targets."""
        summary = self.get_daily_summary(user_id)
        
        # Calculate remaining macros
        remaining = {
            "calories": summary["goals"]["calories"] - summary["totals"]["calories"],
            "protein_g": summary["goals"]["protein_g"] - summary["totals"]["protein_g"],
            "carbs_g": summary["goals"]["carbs_g"] - summary["totals"]["carbs_g"],
            "fat_g": summary["goals"]["fat_g"] - summary["totals"]["fat_g"]
        }
        
        # Suggest based on meal type
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if meal_type == "breakfast":
            c.execute('SELECT * FROM foods WHERE category IN (?, ?, ?)', ('grain', 'fruit', 'dairy'))
        elif meal_type == "lunch" or meal_type == "dinner":
            c.execute('SELECT * FROM foods WHERE category IN (?, ?, ?)', ('protein', 'vegetable', 'grain'))
        else:
            c.execute('SELECT * FROM foods WHERE category IN (?, ?)', ('snack', 'fruit'))
        
        foods = c.fetchall()
        conn.close()
        
        suggestions = []
        for food_row in foods[:5]:
            food = Food(
                id=food_row[0], name=food_row[1], category=food_row[2],
                calories_per_100g=food_row[3], protein_g=food_row[4],
                carbs_g=food_row[5], fat_g=food_row[6]
            )
            
            # Calculate macro match
            portion = min(100, remaining["calories"] / max(food.calories_per_100g, 1))
            
            suggestions.append({
                "food": food.name,
                "food_id": food.id,
                "suggested_grams": round(portion, 0),
                "category": food.category,
                "macros_per_portion": {
                    "calories": round(food.calories_per_100g * portion / 100, 0),
                    "protein_g": round(food.protein_g * portion / 100, 1),
                    "carbs_g": round(food.carbs_g * portion / 100, 1),
                    "fat_g": round(food.fat_g * portion / 100, 1)
                }
            })
        
        return suggestions
    
    def analyze_deficiencies(self, user_id: str, days: int = 7) -> Dict:
        """Analyze nutritional deficiencies over time."""
        deficient_nutrients = {}
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            summary = self.get_daily_summary(user_id, date)
            
            if summary["percentages"]["calories"] < 90:
                deficient_nutrients.setdefault("calories", []).append(summary["percentages"]["calories"])
            if summary["percentages"]["protein"] < 80:
                deficient_nutrients.setdefault("protein", []).append(summary["percentages"]["protein"])
            if summary["percentages"]["carbs"] < 80:
                deficient_nutrients.setdefault("carbs", []).append(summary["percentages"]["carbs"])
            if summary["percentages"]["fat"] < 80:
                deficient_nutrients.setdefault("fat", []).append(summary["percentages"]["fat"])
        
        # Calculate deficiency rates
        analysis = {
            "period_days": days,
            "deficiencies": {}
        }
        
        for nutrient, percentages in deficient_nutrients.items():
            rate = len(percentages) / days * 100
            avg_deficit = 100 - (sum(percentages) / len(percentages))
            analysis["deficiencies"][nutrient] = {
                "deficiency_rate_pct": round(rate, 1),
                "average_deficit_pct": round(avg_deficit, 1),
                "days_deficient": len(percentages)
            }
        
        return analysis


def main():
    parser = argparse.ArgumentParser(description="Nutrition tracking system")
    subparsers = parser.add_subparsers(dest="command")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log a meal")
    log_parser.add_argument("user_id")
    log_parser.add_argument("food_name")
    log_parser.add_argument("grams", type=float)
    log_parser.add_argument("meal_type")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Daily summary")
    summary_parser.add_argument("user_id")
    summary_parser.add_argument("--date", default=None)
    
    # Suggest command
    suggest_parser = subparsers.add_parser("suggest", help="Meal suggestions")
    suggest_parser.add_argument("user_id")
    suggest_parser.add_argument("meal_type")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search foods")
    search_parser.add_argument("query")
    
    # Goals command
    goals_parser = subparsers.add_parser("goals", help="Set goals")
    goals_parser.add_argument("user_id")
    goals_parser.add_argument("--calories", type=int, default=2000)
    goals_parser.add_argument("--protein", type=float, default=50)
    
    args = parser.parse_args()
    tracker = NutritionTracker()
    
    if args.command == "log":
        foods = tracker.search_food(args.food_name)
        if not foods:
            print(f"✗ Food '{args.food_name}' not found")
            return
        
        meal = tracker.log_meal(args.user_id, foods[0].id, args.grams, args.meal_type)
        print(f"✓ Logged: {args.grams}g of {foods[0].name} ({args.meal_type})")
    
    elif args.command == "summary":
        summary = tracker.get_daily_summary(args.user_id, args.date)
        print(f"\n📊 Daily Summary ({summary['date']}):")
        print(json.dumps(summary, indent=2))
    
    elif args.command == "suggest":
        suggestions = tracker.meal_suggestions(args.user_id, args.meal_type)
        print(f"\n🍽 Suggestions for {args.meal_type}:")
        print(json.dumps(suggestions, indent=2, default=str))
    
    elif args.command == "search":
        foods = tracker.search_food(args.query)
        print(f"✓ Found {len(foods)} foods:")
        for food in foods[:10]:
            print(f"  • {food.name} ({food.category}): {food.calories_per_100g} cal/100g")
    
    elif args.command == "goals":
        tracker.set_goals(args.user_id, args.calories, args.protein)
        print(f"✓ Goals set for {args.user_id}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
