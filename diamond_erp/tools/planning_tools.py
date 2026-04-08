"""
Planning Tools - Cutting plans, yield estimation, and worker assignment.
Used by the Planning Agent for diamond manufacturing planning.
"""

from datetime import datetime
from diamond_erp.db import execute_query, execute_read, execute_read_one
from diamond_erp.config import YIELD_ESTIMATES


def create_cutting_plan(
    stone_id: int,
    planned_shape: str,
    assigned_worker_id: int = None,
    priority: str = "normal",
    notes: str = ""
) -> dict:
    """Create a new cutting plan for a rough stone.

    Args:
        stone_id: ID of the rough stone to plan cutting for.
        planned_shape: Target shape (e.g. 'Round Brilliant', 'Princess', 'Cushion').
        assigned_worker_id: Worker ID to assign (optional).
        priority: Priority level - 'normal', 'high', or 'urgent'.
        notes: Optional planning notes.

    Returns:
        dict with plan ID and estimated yield.
    """
    stone = execute_read_one("SELECT * FROM rough_stones WHERE id = ?", (stone_id,))
    if not stone:
        return {"status": "error", "message": f"Stone {stone_id} not found."}
    if stone["status"] not in ("available", "planned"):
        return {"status": "error", "message": f"Stone is '{stone['status']}', cannot create plan."}

    yield_pct = YIELD_ESTIMATES.get(planned_shape, 0.45)
    est_output = round(stone["weight_carat"] * yield_pct, 2)

    plan_id = execute_query(
        """INSERT INTO cutting_plans
           (stone_id, planned_shape, estimated_yield_pct, estimated_output_carat,
            assigned_worker_id, plan_date, status, priority, notes)
           VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
        (stone_id, planned_shape, round(yield_pct * 100, 1), est_output,
         assigned_worker_id, datetime.now().strftime("%Y-%m-%d"), priority, notes)
    )

    # Update stone status
    execute_query("UPDATE rough_stones SET status = 'planned' WHERE id = ?", (stone_id,))

    return {
        "status": "success",
        "message": f"Cutting plan created for stone {stone_id}.",
        "plan_id": plan_id,
        "planned_shape": planned_shape,
        "estimated_yield_pct": round(yield_pct * 100, 1),
        "estimated_output_carat": est_output,
        "rough_weight": stone["weight_carat"]
    }


def get_pending_plans() -> dict:
    """Get all pending cutting plans awaiting execution.

    Returns:
        dict with list of pending plans with stone and worker details.
    """
    rows = execute_read(
        """SELECT cp.*, rs.lot_id, rs.weight_carat as rough_weight, rs.source,
                  w.name as worker_name
           FROM cutting_plans cp
           JOIN rough_stones rs ON cp.stone_id = rs.id
           LEFT JOIN workers w ON cp.assigned_worker_id = w.id
           WHERE cp.status IN ('pending', 'in_progress')
           ORDER BY
             CASE cp.priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 ELSE 3 END,
             cp.plan_date"""
    )
    return {"status": "success", "count": len(rows), "plans": rows}


def estimate_yield(weight_carat: float, planned_shape: str) -> dict:
    """Estimate the polished diamond yield from a rough stone.

    Args:
        weight_carat: Weight of the rough stone in carats.
        planned_shape: Target shape for cutting.

    Returns:
        dict with yield estimate details.
    """
    yield_pct = YIELD_ESTIMATES.get(planned_shape, 0.45)
    est_output = round(weight_carat * yield_pct, 2)
    weight_loss = round(weight_carat - est_output, 2)

    return {
        "status": "success",
        "rough_weight": weight_carat,
        "planned_shape": planned_shape,
        "yield_percentage": round(yield_pct * 100, 1),
        "estimated_polished_carat": est_output,
        "estimated_weight_loss": weight_loss,
        "note": "Actual yield varies based on stone quality, inclusions, and cutter skill."
    }


def assign_worker(plan_id: int, worker_id: int) -> dict:
    """Assign or reassign a worker to a cutting plan.

    Args:
        plan_id: ID of the cutting plan.
        worker_id: ID of the worker to assign.

    Returns:
        dict with assignment confirmation.
    """
    plan = execute_read_one("SELECT * FROM cutting_plans WHERE id = ?", (plan_id,))
    if not plan:
        return {"status": "error", "message": f"Plan {plan_id} not found."}

    worker = execute_read_one("SELECT * FROM workers WHERE id = ?", (worker_id,))
    if not worker:
        return {"status": "error", "message": f"Worker {worker_id} not found."}

    execute_query(
        "UPDATE cutting_plans SET assigned_worker_id = ? WHERE id = ?",
        (worker_id, plan_id)
    )
    return {
        "status": "success",
        "message": f"Worker '{worker['name']}' assigned to plan {plan_id}."
    }


def get_all_plans(status: str = "") -> dict:
    """Get all cutting plans, optionally filtered by status.

    Args:
        status: Filter by status (pending, in_progress, completed). Empty for all.

    Returns:
        dict with list of plans.
    """
    sql = """SELECT cp.*, rs.lot_id, rs.weight_carat as rough_weight,
                    w.name as worker_name
             FROM cutting_plans cp
             JOIN rough_stones rs ON cp.stone_id = rs.id
             LEFT JOIN workers w ON cp.assigned_worker_id = w.id"""
    params = []

    if status:
        sql += " WHERE cp.status = ?"
        params.append(status)

    sql += " ORDER BY cp.plan_date DESC"
    rows = execute_read(sql, tuple(params))
    return {"status": "success", "count": len(rows), "plans": rows}
