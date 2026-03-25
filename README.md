<!-- BlackRoad SEO Enhanced -->

# ulackroad nutrition tracker

> Part of **[BlackRoad OS](https://blackroad.io)** — Sovereign Computing for Everyone

[![BlackRoad OS](https://img.shields.io/badge/BlackRoad-OS-ff1d6c?style=for-the-badge)](https://blackroad.io)
[![BlackRoad OS](https://img.shields.io/badge/Org-BlackRoad-OS-2979ff?style=for-the-badge)](https://github.com/BlackRoad-OS)
[![License](https://img.shields.io/badge/License-Proprietary-f5a623?style=for-the-badge)](LICENSE)

**ulackroad nutrition tracker** is part of the **BlackRoad OS** ecosystem — a sovereign, distributed operating system built on edge computing, local AI, and mesh networking by **BlackRoad OS, Inc.**

## About BlackRoad OS

BlackRoad OS is a sovereign computing platform that runs AI locally on your own hardware. No cloud dependencies. No API keys. No surveillance. Built by [BlackRoad OS, Inc.](https://github.com/BlackRoad-OS-Inc), a Delaware C-Corp founded in 2025.

### Key Features
- **Local AI** — Run LLMs on Raspberry Pi, Hailo-8, and commodity hardware
- **Mesh Networking** — WireGuard VPN, NATS pub/sub, peer-to-peer communication
- **Edge Computing** — 52 TOPS of AI acceleration across a Pi fleet
- **Self-Hosted Everything** — Git, DNS, storage, CI/CD, chat — all sovereign
- **Zero Cloud Dependencies** — Your data stays on your hardware

### The BlackRoad Ecosystem
| Organization | Focus |
|---|---|
| [BlackRoad OS](https://github.com/BlackRoad-OS) | Core platform and applications |
| [BlackRoad OS, Inc.](https://github.com/BlackRoad-OS-Inc) | Corporate and enterprise |
| [BlackRoad AI](https://github.com/BlackRoad-AI) | Artificial intelligence and ML |
| [BlackRoad Hardware](https://github.com/BlackRoad-Hardware) | Edge hardware and IoT |
| [BlackRoad Security](https://github.com/BlackRoad-Security) | Cybersecurity and auditing |
| [BlackRoad Quantum](https://github.com/BlackRoad-Quantum) | Quantum computing research |
| [BlackRoad Agents](https://github.com/BlackRoad-Agents) | Autonomous AI agents |
| [BlackRoad Network](https://github.com/BlackRoad-Network) | Mesh and distributed networking |
| [BlackRoad Education](https://github.com/BlackRoad-Education) | Learning and tutoring platforms |
| [BlackRoad Labs](https://github.com/BlackRoad-Labs) | Research and experiments |
| [BlackRoad Cloud](https://github.com/BlackRoad-Cloud) | Self-hosted cloud infrastructure |
| [BlackRoad Forge](https://github.com/BlackRoad-Forge) | Developer tools and utilities |

### Links
- **Website**: [blackroad.io](https://blackroad.io)
- **Documentation**: [docs.blackroad.io](https://docs.blackroad.io)
- **Chat**: [chat.blackroad.io](https://chat.blackroad.io)
- **Search**: [search.blackroad.io](https://search.blackroad.io)

---


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
