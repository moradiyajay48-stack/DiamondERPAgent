"""
Inventory Tools - Rough stone intake and stock management.
Used by the Inventory Agent for managing diamond rough stone inventory.
"""

from datetime import datetime
from diamond_erp.db import execute_query, execute_read, execute_read_one


def add_rough_stone(
    lot_id: str,
    weight_carat: float,
    source: str,
    color_raw: str,
    purchase_price: float,
    supplier: str = "",
    shape_raw: str = "Octahedron",
    notes: str = ""
) -> dict:
    """Register a new rough diamond stone into inventory.

    Args:
        lot_id: Unique lot identifier (e.g. 'RS-021').
        weight_carat: Weight in carats.
        source: Origin/mine (e.g. 'Botswana - De Beers').
        color_raw: Raw color description (e.g. 'White', 'Near White').
        purchase_price: Purchase price in USD.
        supplier: Supplier company name.
        shape_raw: Raw crystal shape (e.g. 'Octahedron', 'Macle').
        notes: Optional notes.

    Returns:
        dict with status and the new stone ID.
    """
    try:
        stone_id = execute_query(
            """INSERT INTO rough_stones
               (lot_id, weight_carat, source, color_raw, shape_raw, purchase_price, purchase_date, supplier, status, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'available', ?)""",
            (lot_id, weight_carat, source, color_raw, shape_raw, purchase_price,
             datetime.now().strftime("%Y-%m-%d"), supplier, notes)
        )
        return {"status": "success", "message": f"Rough stone {lot_id} added successfully.", "stone_id": stone_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_inventory_summary() -> dict:
    """Get overall inventory summary showing stone counts and values by status.

    Returns:
        dict with inventory breakdown by status, total stones, and total value.
    """
    rows = execute_read(
        """SELECT status, COUNT(*) as count, 
           ROUND(SUM(weight_carat), 2) as total_carats,
           ROUND(SUM(purchase_price), 2) as total_value
           FROM rough_stones GROUP BY status ORDER BY count DESC"""
    )
    total = execute_read_one(
        """SELECT COUNT(*) as total_stones, 
           ROUND(SUM(weight_carat), 2) as total_carats,
           ROUND(SUM(purchase_price), 2) as total_value
           FROM rough_stones"""
    )
    return {
        "status": "success",
        "by_status": rows,
        "totals": total
    }


def search_stones(
    status: str = "",
    min_carat: float = 0,
    max_carat: float = 999,
    source: str = ""
) -> dict:
    """Search rough stones with optional filters.

    Args:
        status: Filter by status (e.g. 'available', 'planned', 'in_process'). Empty for all.
        min_carat: Minimum carat weight.
        max_carat: Maximum carat weight.
        source: Filter by source/origin (partial match). Empty for all.

    Returns:
        dict with matching stones list.
    """
    sql = "SELECT * FROM rough_stones WHERE weight_carat BETWEEN ? AND ?"
    params = [min_carat, max_carat]

    if status:
        sql += " AND status = ?"
        params.append(status)
    if source:
        sql += " AND source LIKE ?"
        params.append(f"%{source}%")

    sql += " ORDER BY weight_carat DESC"
    rows = execute_read(sql, tuple(params))
    return {"status": "success", "count": len(rows), "stones": rows}


def get_stone_details(stone_id: int) -> dict:
    """Get detailed information about a specific rough stone.

    Args:
        stone_id: The database ID of the rough stone.

    Returns:
        dict with full stone details including any associated plans.
    """
    stone = execute_read_one("SELECT * FROM rough_stones WHERE id = ?", (stone_id,))
    if not stone:
        return {"status": "error", "message": f"Stone with ID {stone_id} not found."}

    plans = execute_read(
        "SELECT * FROM cutting_plans WHERE stone_id = ?", (stone_id,)
    )
    return {"status": "success", "stone": stone, "cutting_plans": plans}


def update_stone_status(stone_id: int, new_status: str) -> dict:
    """Update the status of a rough stone.

    Args:
        stone_id: The database ID of the stone.
        new_status: New status value (available, planned, in_process, polished, graded, certified, sold).

    Returns:
        dict with update confirmation.
    """
    valid = ["available", "planned", "in_process", "polished", "graded", "certified", "sold"]
    if new_status not in valid:
        return {"status": "error", "message": f"Invalid status. Must be one of: {valid}"}

    execute_query(
        "UPDATE rough_stones SET status = ? WHERE id = ?",
        (new_status, stone_id)
    )
    return {"status": "success", "message": f"Stone {stone_id} status updated to '{new_status}'."}
