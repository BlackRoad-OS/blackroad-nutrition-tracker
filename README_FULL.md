# BlackRoad Nutrition Tracker

Comprehensive nutrition tracking and meal planning system for personal nutrition management with AI-powered insights.

## Features

### 🍽️ Meal Logging
- Log meals with precise portion control
- 4 meal types: Breakfast, Lunch, Dinner, Snack
- Flexible date selection
- Custom notes per meal
- Automatic macro calculation

### 🥗 Food Database
- **20 Pre-populated Foods**:
  - Fruits: Apple, Banana, Orange, Blueberries
  - Vegetables: Broccoli, Spinach, Sweet Potato
  - Proteins: Chicken Breast, Eggs, Salmon, Lentils
  - Grains: Rice, Oats, Bread, Pasta
  - Dairy: Greek Yogurt, Milk, Cheese
  - Fats: Almonds, Olive Oil

- **Custom Food Addition**: Add any food with detailed nutritional info
- **Search**: Find foods by name or category
- **Macro Details**: Calories, protein, carbs, fat, fiber, sugar, sodium

### 📊 Nutrition Analysis
- **Daily Summary**:
  - Total macros vs. daily targets
  - Percentage of goals achieved
  - Meal count
  
- **Weekly Report**:
  - 7-day trends
  - Average macro intake
  - Consistency tracking
  
- **Deficiency Analysis**:
  - Identify consistently low nutrients
  - Deficiency rates over time
  - Specific recommendations

### 🎯 Goal Setting
- Customizable daily targets
- Default: 2000 cal, 50g protein, 260g carbs, 65g fat
- Per-user profiles
- Easy adjustments

### 💡 Smart Suggestions
- Meal-type-specific recommendations
- Macros to hit remaining daily targets
- Category-appropriate suggestions
- Portion recommendations

### 🔍 Search & Discovery
- Fast food search
- Category filtering
- Nutritional comparison
- Macro-based discovery

## Installation

```bash
git clone https://github.com/BlackRoad-OS/blackroad-nutrition-tracker.git
cd blackroad-nutrition-tracker
pip install -e .
```

## Usage

### Log a Meal
```bash
python src/nutrition.py log user1 chicken_breast 150 lunch
```

Output:
```
✓ Logged: 150g of Chicken Breast (lunch)
```

### View Daily Summary
```bash
python src/nutrition.py summary user1
```

Output:
```json
{
  "date": "2024-01-15",
  "totals": {
    "calories": 1850.5,
    "protein_g": 45.2,
    "carbs_g": 210.0,
    "fat_g": 58.3
  },
  "goals": {
    "calories": 2000,
    "protein_g": 50,
    "carbs_g": 260,
    "fat_g": 65
  },
  "percentages": {
    "calories": 92.5,
    "protein": 90.4,
    "carbs": 80.8,
    "fat": 89.7
  },
  "meal_count": 3
}
```

### Get Meal Suggestions
```bash
python src/nutrition.py suggest user1 dinner
```

Output:
```json
[
  {
    "food": "salmon",
    "food_id": "F_ABC12345",
    "suggested_grams": 150,
    "category": "protein",
    "macros_per_portion": {
      "calories": 312,
      "protein_g": 30,
      "carbs_g": 0,
      "fat_g": 20
    }
  }
]
```

### Search Foods
```bash
python src/nutrition.py search apple
python src/nutrition.py search protein
```

### Set Daily Goals
```bash
python src/nutrition.py goals user1 --calories 2200 --protein 60
```

## Database

SQLite database stored at `~/.blackroad/nutrition.db`

### Schema
- **foods**: Food nutritional database
- **meals**: User meal entries
- **goals**: User-specific daily targets

## Python API

### Basic Usage
```python
from src.nutrition import NutritionTracker

tracker = NutritionTracker()

# Set goals for a user
tracker.set_goals("user1", calories=2000, protein=50, carbs=260, fat=65)

# Find a food
foods = tracker.search_food("chicken")
food_id = foods[0].id

# Log a meal
meal = tracker.log_meal("user1", food_id, 150, "lunch")
print(f"Logged: {meal.grams}g of {foods[0].name}")

# Get daily summary
summary = tracker.get_daily_summary("user1")
print(f"Calories: {summary['totals']['calories']:.0f}/{summary['goals']['calories']}")
print(f"Protein: {summary['percentages']['protein']:.1f}%")

# Get meal suggestions
suggestions = tracker.meal_suggestions("user1", "dinner")
for sugg in suggestions:
    print(f"Suggested: {sugg['food']} ({sugg['suggested_grams']}g)")

# Get 7-day report
weekly = tracker.get_weekly_report("user1")
print(f"Weekly avg calories: {weekly['averages']['calories']:.0f}")

# Analyze deficiencies
deficiencies = tracker.analyze_deficiencies("user1", days=7)
for nutrient, data in deficiencies['deficiencies'].items():
    print(f"{nutrient}: deficient {data['days_deficient']} days")

# Add custom food
food = tracker.add_food(
    name="quinoa",
    category="grain",
    cal=120,
    protein=4.4,
    carbs=21,
    fat=1.9,
    fiber=2.8
)
```

## Food Categories

- **Fruit**: Apples, bananas, berries, citrus
- **Vegetable**: Greens, root vegetables, cruciferous
- **Grain**: Rice, oats, bread, pasta
- **Protein**: Meat, fish, eggs, legumes
- **Dairy**: Milk, yogurt, cheese
- **Fat**: Oils, nuts, seeds
- **Beverage**: Water, juice, coffee
- **Snack**: Processed, convenience foods

## Nutrition Targets

### Macronutrient Balance (Default 2000 cal)
- **Protein**: 50g (10% of calories)
- **Carbohydrates**: 260g (52% of calories)
- **Fat**: 65g (29% of calories)
- **Fiber**: 25g

### Micronutrient Basics
- Vitamins: A, D, E, K, C, B-complex
- Minerals: Iron, zinc, magnesium, calcium
- Electrolytes: Sodium, potassium

## CLI Commands

```bash
# Log a meal
python src/nutrition.py log <user_id> <food_name> <grams> <meal_type>

# Daily summary
python src/nutrition.py summary <user_id> [--date YYYY-MM-DD]

# Meal suggestions
python src/nutrition.py suggest <user_id> <meal_type>

# Search foods
python src/nutrition.py search <query>

# Set goals
python src/nutrition.py goals <user_id> [--calories N] [--protein G]
```

## Advanced Features

### Deficiency Tracking
Identifies nutrients consistently below target:
```python
analysis = tracker.analyze_deficiencies("user1", days=7)
# Output: {"deficiencies": {"protein": {"deficiency_rate_pct": 28.6, ...}}}
```

### Weekly Trends
```python
weekly = tracker.get_weekly_report("user1")
# Shows 7-day patterns and averages
```

### Smart Portions
Suggestions automatically calculate optimal portions based on:
- Remaining daily macros
- Meal type preferences
- Nutritional density

## Use Cases

- Personal fitness nutrition tracking
- Weight management monitoring
- Sports nutrition planning
- Dietary restriction management
- Meal prep optimization
- Nutrition deficiency identification
- Healthy habit formation

## Data Privacy

- User data stored locally in SQLite
- No cloud synchronization
- Personal nutrition data not shared
- Local computation only

## Limitations

This is an educational tool:
- Simplified macronutrient model
- No micronutrient tracking
- No barcode scanning
- No recipe parsing
- Basic portion estimation
- No AI learning algorithms

Real-world nutrition involves:
- Individual bioavailability
- Food-nutrient interactions
- Seasonal variations
- Individual health conditions
- Professional guidance

## License

MIT
