"""
Diamond ERP Database Setup
Creates all tables and seeds with realistic sample data.
Run: python setup_database.py
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
DB_PATH = os.path.join("data", "diamond_erp.db")

# Remove existing DB for clean setup
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ============================================================
# SCHEMA
# ============================================================

cursor.executescript("""
-- Workers / Employees
CREATE TABLE IF NOT EXISTS workers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    department TEXT NOT NULL,
    hire_date TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    phone TEXT,
    email TEXT
);

-- Rough Stones Inventory
CREATE TABLE IF NOT EXISTS rough_stones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id TEXT UNIQUE NOT NULL,
    weight_carat REAL NOT NULL,
    source TEXT NOT NULL,
    color_raw TEXT,
    shape_raw TEXT,
    purchase_price REAL NOT NULL,
    purchase_date TEXT NOT NULL,
    supplier TEXT,
    status TEXT DEFAULT 'available',
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Cutting / Manufacturing Plans
CREATE TABLE IF NOT EXISTS cutting_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stone_id INTEGER NOT NULL,
    planned_shape TEXT NOT NULL,
    estimated_yield_pct REAL,
    estimated_output_carat REAL,
    assigned_worker_id INTEGER,
    plan_date TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'normal',
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stone_id) REFERENCES rough_stones(id),
    FOREIGN KEY (assigned_worker_id) REFERENCES workers(id)
);

-- Production Processes (each step in manufacturing)
CREATE TABLE IF NOT EXISTS production_processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    process_type TEXT NOT NULL,
    worker_id INTEGER,
    start_time TEXT,
    end_time TEXT,
    weight_before REAL,
    weight_after REAL,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES cutting_plans(id),
    FOREIGN KEY (worker_id) REFERENCES workers(id)
);

-- Polished Diamonds (finished products)
CREATE TABLE IF NOT EXISTS polished_diamonds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stone_id INTEGER NOT NULL,
    shape TEXT NOT NULL,
    weight_carat REAL NOT NULL,
    color TEXT,
    clarity TEXT,
    cut_grade TEXT,
    fluorescence TEXT DEFAULT 'None',
    measurements TEXT,
    status TEXT DEFAULT 'available',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stone_id) REFERENCES rough_stones(id)
);

-- Grading Reports
CREATE TABLE IF NOT EXISTS grading_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    diamond_id INTEGER NOT NULL,
    grader TEXT NOT NULL,
    grade_date TEXT NOT NULL,
    color_grade TEXT NOT NULL,
    clarity_grade TEXT NOT NULL,
    cut_grade TEXT NOT NULL,
    carat_weight REAL NOT NULL,
    certificate_number TEXT UNIQUE,
    lab TEXT DEFAULT 'GIA',
    polish TEXT,
    symmetry TEXT,
    fluorescence TEXT,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (diamond_id) REFERENCES polished_diamonds(id)
);

-- Sales Records
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    diamond_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    customer_email TEXT,
    customer_phone TEXT,
    sale_price REAL NOT NULL,
    cost_price REAL,
    sale_date TEXT NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    payment_status TEXT DEFAULT 'pending',
    payment_method TEXT,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (diamond_id) REFERENCES polished_diamonds(id)
);
""")

# ============================================================
# SEED DATA
# ============================================================

now = datetime.now()

# --- Workers ---
workers = [
    ("Rajesh Patel", "Master Cutter", "Production", (now - timedelta(days=1825)).strftime("%Y-%m-%d"), "active", "+91-9876543210", "rajesh@diamonderp.com"),
    ("Suresh Shah", "Senior Polisher", "Production", (now - timedelta(days=1460)).strftime("%Y-%m-%d"), "active", "+91-9876543211", "suresh@diamonderp.com"),
    ("Amit Mehta", "Diamond Grader", "Quality", (now - timedelta(days=1095)).strftime("%Y-%m-%d"), "active", "+91-9876543212", "amit@diamonderp.com"),
    ("Priya Desai", "Production Planner", "Planning", (now - timedelta(days=730)).strftime("%Y-%m-%d"), "active", "+91-9876543213", "priya@diamonderp.com"),
    ("Vikram Joshi", "Sales Manager", "Sales", (now - timedelta(days=1200)).strftime("%Y-%m-%d"), "active", "+91-9876543214", "vikram@diamonderp.com"),
    ("Anita Sharma", "Junior Cutter", "Production", (now - timedelta(days=365)).strftime("%Y-%m-%d"), "active", "+91-9876543215", "anita@diamonderp.com"),
    ("Deepak Kumar", "Bruter", "Production", (now - timedelta(days=900)).strftime("%Y-%m-%d"), "active", "+91-9876543216", "deepak@diamonderp.com"),
]
cursor.executemany(
    "INSERT INTO workers (name, role, department, hire_date, status, phone, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
    workers
)

# --- Rough Stones ---
sources = ["Botswana - De Beers", "Russia - ALROSA", "Canada - Diavik", "South Africa - Cullinan", "Angola - Catoca", "Sierra Leone", "Lesotho"]
colors_raw = ["White", "Near White", "Light Yellow", "Cape", "Fancy Yellow", "Silver Cape", "Top White"]
shapes_raw = ["Octahedron", "Dodecahedron", "Macle", "Irregular", "Flat", "Elongated"]

rough_stones = []
for i in range(1, 21):
    lot_id = f"RS-{i:03d}"
    weight = round(random.uniform(0.5, 12.0), 2)
    source = random.choice(sources)
    color = random.choice(colors_raw)
    shape = random.choice(shapes_raw)
    price = round(weight * random.uniform(800, 5000), 2)
    date = (now - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d")
    supplier = source.split(" - ")[0] + " Mining Corp"

    # Assign varied statuses
    if i <= 8:
        status = "available"
    elif i <= 12:
        status = "planned"
    elif i <= 16:
        status = "in_process"
    elif i <= 18:
        status = "polished"
    else:
        status = "sold"

    rough_stones.append((lot_id, weight, source, color, shape, price, date, supplier, status, None))

cursor.executemany(
    "INSERT INTO rough_stones (lot_id, weight_carat, source, color_raw, shape_raw, purchase_price, purchase_date, supplier, status, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    rough_stones
)

# --- Cutting Plans (for planned & in_process stones) ---
planned_shapes = ["Round Brilliant", "Princess", "Cushion", "Oval", "Emerald", "Pear", "Marquise", "Radiant"]
yield_pcts = {"Round Brilliant": 42, "Princess": 50, "Cushion": 48, "Oval": 52, "Emerald": 55, "Pear": 45, "Marquise": 44, "Radiant": 48}

for stone_id in range(9, 19):  # stones 9-18 have plans
    shape = random.choice(planned_shapes)
    stone_weight = cursor.execute("SELECT weight_carat FROM rough_stones WHERE id=?", (stone_id,)).fetchone()[0]
    yield_pct = yield_pcts[shape]
    est_output = round(stone_weight * yield_pct / 100, 2)
    worker_id = random.choice([1, 2, 6, 7])
    plan_date = (now - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")

    if stone_id <= 12:
        plan_status = "pending"
    elif stone_id <= 16:
        plan_status = "in_progress"
    else:
        plan_status = "completed"

    cursor.execute(
        "INSERT INTO cutting_plans (stone_id, planned_shape, estimated_yield_pct, estimated_output_carat, assigned_worker_id, plan_date, status, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (stone_id, shape, yield_pct, est_output, worker_id, plan_date, plan_status, random.choice(["normal", "high", "urgent"]))
    )

# --- Production Processes (for in_progress plans) ---
process_types = ["sawing", "bruting", "cutting", "polishing"]
for plan_id in range(5, 9):  # plans 5-8 are in_progress
    plan_row = cursor.execute("SELECT stone_id, estimated_output_carat FROM cutting_plans WHERE id=?", (plan_id,)).fetchone()
    if plan_row:
        stone_weight = cursor.execute("SELECT weight_carat FROM rough_stones WHERE id=?", (plan_row[0],)).fetchone()[0]
        current_weight = stone_weight
        for j, proc in enumerate(process_types[:random.randint(1, 3)]):
            w_before = current_weight
            w_after = round(w_before * random.uniform(0.75, 0.95), 2)
            current_weight = w_after
            start = (now - timedelta(days=random.randint(1, 15), hours=random.randint(1, 8))).strftime("%Y-%m-%d %H:%M")
            end = (now - timedelta(days=random.randint(0, 5), hours=random.randint(1, 8))).strftime("%Y-%m-%d %H:%M") if j < 2 else None
            status = "completed" if end else "in_progress"
            cursor.execute(
                "INSERT INTO production_processes (plan_id, process_type, worker_id, start_time, end_time, weight_before, weight_after, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (plan_id, proc, random.choice([1, 2, 6, 7]), start, end, w_before, w_after if end else None, status)
            )

# --- Polished Diamonds (for completed stones) ---
colors = ["D", "E", "F", "G", "H"]
clarities = ["FL", "IF", "VVS1", "VVS2", "VS1", "VS2"]
cuts = ["Excellent", "Very Good", "Good"]

for stone_id in [17, 18, 19, 20]:
    stone_row = cursor.execute("SELECT weight_carat FROM rough_stones WHERE id=?", (stone_id,)).fetchone()
    if stone_row:
        polished_weight = round(stone_row[0] * random.uniform(0.38, 0.55), 2)
        shape = random.choice(planned_shapes)
        cursor.execute(
            "INSERT INTO polished_diamonds (stone_id, shape, weight_carat, color, clarity, cut_grade, fluorescence, measurements, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (stone_id, shape, polished_weight, random.choice(colors), random.choice(clarities),
             random.choice(cuts), random.choice(["None", "Faint"]),
             f"{round(random.uniform(4, 9), 2)}x{round(random.uniform(4, 9), 2)}x{round(random.uniform(2.5, 5.5), 2)}mm",
             "available" if stone_id <= 18 else "sold")
        )

# --- Grading Reports (for some polished diamonds) ---
for diamond_id in [1, 2]:
    diamond_row = cursor.execute("SELECT weight_carat, color, clarity, cut_grade, fluorescence FROM polished_diamonds WHERE id=?", (diamond_id,)).fetchone()
    if diamond_row:
        cert_num = f"GIA-{random.randint(100000000, 999999999)}"
        cursor.execute(
            "INSERT INTO grading_reports (diamond_id, grader, grade_date, color_grade, clarity_grade, cut_grade, carat_weight, certificate_number, lab, polish, symmetry, fluorescence) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (diamond_id, "Amit Mehta", (now - timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d"),
             diamond_row[1], diamond_row[2], diamond_row[3], diamond_row[0], cert_num, "GIA",
             random.choice(["Excellent", "Very Good"]), random.choice(["Excellent", "Very Good"]), diamond_row[4])
        )

# --- Sales (for sold stones) ---
for diamond_id in [3, 4]:
    diamond_row = cursor.execute("SELECT weight_carat FROM polished_diamonds WHERE id=?", (diamond_id,)).fetchone()
    if diamond_row:
        sale_price = round(diamond_row[0] * random.uniform(5000, 15000), 2)
        cost_price = round(sale_price * random.uniform(0.5, 0.7), 2)
        inv_num = f"INV-{now.year}-{random.randint(1000, 9999)}"
        cursor.execute(
            "INSERT INTO sales (diamond_id, customer_name, customer_email, sale_price, cost_price, sale_date, invoice_number, payment_status, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (diamond_id, random.choice(["Tiffany & Co.", "Cartier", "Harry Winston", "Bharat Diamonds"]),
             "buyer@example.com", sale_price, cost_price,
             (now - timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d"),
             inv_num, "paid", random.choice(["wire_transfer", "check"]))
        )

conn.commit()

# ============================================================
# VERIFICATION
# ============================================================
print("=" * 60)
print("  [*] Diamond ERP Database Setup Complete!")
print("=" * 60)

tables = ["workers", "rough_stones", "cutting_plans", "production_processes", "polished_diamonds", "grading_reports", "sales"]
for table in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  [OK] {table:25s} -> {count} records")

print("=" * 60)
print(f"  Database: {DB_PATH}")
print("=" * 60)

conn.close()
