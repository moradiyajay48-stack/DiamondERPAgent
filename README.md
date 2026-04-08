# 💎 Diamond Manufacturing ERP — Multi-Agent System

A comprehensive **multi-agent ERP system** for diamond manufacturing, built with **Google Agent Development Kit (ADK)**. The system uses 6 specialized AI agents orchestrated by a central coordinator to manage the complete diamond lifecycle — from rough stone intake to polished gem certification and sales.

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │   💎 ERP Orchestrator Agent      │
                    │   (Root Coordinator)             │
                    └──────────────┬──────────────────┘
                                   │
         ┌─────────┬───────┬───────┼───────┬─────────┬──────────┐
         │         │       │       │       │         │          │
    ┌────▼───┐ ┌───▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌───▼────┐
    │Inventory│ │Plan- │ │Prod-│ │Grad-│ │Sales│ │Report- │
    │ Agent   │ │ning  │ │uction│ │ing  │ │Agent│ │ing     │
    │         │ │Agent │ │Agent│ │Agent│ │     │ │Agent   │
    └────┬───┘ └───┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └───┬────┘
         │         │       │       │       │         │
    ┌────▼───┐ ┌───▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌───▼────┐
    │5 Tools │ │5 Tools│ │5 Tools│ │4 Tools│ │5 Tools│ │5 Tools │
    └────────┘ └──────┘ └─────┘ └─────┘ └─────┘ └────────┘
                                   │
                          ┌────────▼────────┐
                          │  SQLite Database │
                          │  (7 Tables)      │
                          └─────────────────┘
```

### Diamond Manufacturing Lifecycle
```
Rough Purchase → Inventory → Planning → Sawing → Bruting → Cutting → Polishing → Grading → Certification → Sales
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Google Gemini API Key** — Get free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 1. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Your API Key
Edit the `.env` file and add your Gemini API key:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

### 4. Initialize Database
```bash
python setup_database.py
```
This creates the SQLite database with 7 tables and seeds it with realistic sample data (20 rough stones, 7 workers, cutting plans, polished diamonds, and sales records).

### 5. Run the Agent System
```bash
# Web Interface (recommended)
adk web .

# Command Line Interface
adk run diamond_erp
```

The web UI will open at `http://localhost:8000` — select `diamond_erp` from the agent dropdown.

## 💬 Example Queries

### Inventory
- "Show me the current inventory summary"
- "Add a new rough stone: 3.5 carat, from Botswana, White color, $12,000"
- "Search for available stones over 5 carats"
- "What's the status of stone RS-005?"

### Planning
- "Create a cutting plan for stone 3 with Round Brilliant shape"
- "What would be the estimated yield for a 4 carat round brilliant?"
- "Show all pending cutting plans"
- "Assign worker Rajesh to plan 2"

### Production
- "Start sawing process for plan 5 with worker 1"
- "Complete process 3 with output weight 2.8 carats"
- "Show all active manufacturing processes"
- "Register a polished diamond from stone 17: Round Brilliant, 1.52 carats"

### Grading
- "Grade diamond 1 with color D, clarity VS1, cut Excellent, graded by Amit"
- "Show the grading report for diamond 2"
- "List all ungraded diamonds"

### Sales
- "Search for available round brilliant diamonds over 1 carat"
- "Calculate the price for diamond 1 at $8,500 per carat"
- "Create an invoice for diamond 1 to Tiffany & Co. at $15,000"
- "Show sales history for the last 30 days"

### Reports
- "Generate an inventory report"
- "Show me the production report"
- "Give me a sales report for the last 90 days"
- "Generate a profit and loss report"
- "Show worker productivity for all workers"

## 📦 Project Structure

```
DiamondERPAgent/
├── .env                          # API key configuration
├── requirements.txt              # Python dependencies
├── setup_database.py             # Database schema + seed data
├── README.md                     # This file
├── diamond_erp/                  # Main ADK agent package
│   ├── __init__.py               # Exports root_agent
│   ├── agent.py                  # Root orchestrator agent
│   ├── config.py                 # Configuration & constants
│   ├── db.py                     # Database helper
│   ├── prompts.py                # All agent prompts
│   ├── tools/                    # Tool functions
│   │   ├── inventory_tools.py    # 5 tools: add, search, details, summary, status
│   │   ├── planning_tools.py     # 5 tools: plan, estimate, assign, pending, all
│   │   ├── production_tools.py   # 5 tools: start, complete, active, history, register
│   │   ├── grading_tools.py      # 4 tools: grade, report, ungraded, update
│   │   ├── sales_tools.py        # 5 tools: search, price, invoice, payment, history
│   │   └── reporting_tools.py    # 5 tools: inventory, production, sales, P&L, workers
│   └── sub_agents/               # Specialist agents
│       ├── inventory_agent.py
│       ├── planning_agent.py
│       ├── production_agent.py
│       ├── grading_agent.py
│       ├── sales_agent.py
│       └── reporting_agent.py
└── data/
    └── diamond_erp.db            # SQLite database (auto-created)
```

## 🗄️ Database Schema

| Table | Records | Description |
|-------|---------|-------------|
| `workers` | 7 | Employee registry with roles and departments |
| `rough_stones` | 20 | Rough diamond inventory with source, weight, pricing |
| `cutting_plans` | 10 | Manufacturing plans with shape, yield, worker assignment |
| `production_processes` | ~12 | Process steps (sawing, bruting, cutting, polishing) |
| `polished_diamonds` | 4 | Finished product inventory with 4Cs |
| `grading_reports` | 2 | GIA-style grading certificates |
| `sales` | 2 | Sales records with invoicing and payments |

## 🔧 Technology Stack

- **[Google ADK](https://google.github.io/adk-docs/)** — Agent Development Kit for multi-agent orchestration
- **[Gemini 2.0 Flash](https://ai.google.dev/)** — LLM powering all agents
- **SQLite** — Lightweight embedded database
- **Python 3.10+** — Runtime

## 📄 License

MIT License
