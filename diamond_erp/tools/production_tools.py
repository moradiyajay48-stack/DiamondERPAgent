"""
Production Tools - Manufacturing process tracking.
Used by the Production Agent to manage sawing, bruting, cutting, and polishing.
"""

from datetime import datetime
from diamond_erp.db import execute_query, execute_read, execute_read_one


def start_process(
    plan_id: int,
    process_type: str,
    worker_id: int,
    weight_before: float = None
) -> dict:
    """Start a new manufacturing process step for a cutting plan.

    Args:
        plan_id: ID of the cutting plan.
        process_type: Type of process - 'sawing', 'bruting', 'cutting', or 'polishing'.
        worker_id: ID of the worker performing the process.
        weight_before: Weight in carats before this process step. If not provided, uses last known weight.

    Returns:
        dict with process ID and confirmation.
    """
    valid_types = ["sawing", "bruting", "cutting", "polishing"]
    if process_type not in valid_types:
        return {"status": "error", "message": f"Invalid process type. Must be one of: {valid_types}"}

    plan = execute_read_one(
        """SELECT cp.*, rs.weight_carat as rough_weight
           FROM cutting_plans cp
           JOIN rough_stones rs ON cp.stone_id = rs.id
           WHERE cp.id = ?""",
        (plan_id,)
    )
    if not plan:
        return {"status": "error", "message": f"Plan {plan_id} not found."}

    # Get the latest weight from previous processes
    if weight_before is None:
        last_proc = execute_read_one(
            """SELECT weight_after FROM production_processes
               WHERE plan_id = ? AND status = 'completed' AND weight_after IS NOT NULL
               ORDER BY id DESC LIMIT 1""",
            (plan_id,)
        )
        weight_before = last_proc["weight_after"] if last_proc else plan["rough_weight"]

    process_id = execute_query(
        """INSERT INTO production_processes
           (plan_id, process_type, worker_id, start_time, weight_before, status)
           VALUES (?, ?, ?, ?, ?, 'in_progress')""",
        (plan_id, process_type, worker_id, datetime.now().strftime("%Y-%m-%d %H:%M"), weight_before)
    )

    # Update plan status
    execute_query("UPDATE cutting_plans SET status = 'in_progress' WHERE id = ?", (plan_id,))
    # Update stone status
    execute_query(
        "UPDATE rough_stones SET status = 'in_process' WHERE id = ?",
        (plan["stone_id"],)
    )

    return {
        "status": "success",
        "message": f"{process_type.capitalize()} process started for plan {plan_id}.",
        "process_id": process_id,
        "weight_before": weight_before
    }


def complete_process(
    process_id: int,
    weight_after: float,
    notes: str = ""
) -> dict:
    """Complete a manufacturing process step and record the output weight.

    Args:
        process_id: ID of the production process to complete.
        weight_after: Weight in carats after this process step.
        notes: Optional notes about the process.

    Returns:
        dict with completion details and weight loss.
    """
    process = execute_read_one(
        "SELECT * FROM production_processes WHERE id = ?", (process_id,)
    )
    if not process:
        return {"status": "error", "message": f"Process {process_id} not found."}
    if process["status"] == "completed":
        return {"status": "error", "message": "Process is already completed."}

    weight_loss = round(process["weight_before"] - weight_after, 2) if process["weight_before"] else 0
    loss_pct = round((weight_loss / process["weight_before"]) * 100, 1) if process["weight_before"] else 0

    execute_query(
        """UPDATE production_processes
           SET weight_after = ?, end_time = ?, status = 'completed', notes = ?
           WHERE id = ?""",
        (weight_after, datetime.now().strftime("%Y-%m-%d %H:%M"), notes, process_id)
    )

    return {
        "status": "success",
        "message": f"Process {process_id} completed.",
        "process_type": process["process_type"],
        "weight_before": process["weight_before"],
        "weight_after": weight_after,
        "weight_loss": weight_loss,
        "loss_percentage": loss_pct
    }


def get_active_processes() -> dict:
    """Get all currently active (in-progress) manufacturing processes.

    Returns:
        dict with list of active processes with plan and worker details.
    """
    rows = execute_read(
        """SELECT pp.*, cp.planned_shape, cp.stone_id, rs.lot_id,
                  w.name as worker_name
           FROM production_processes pp
           JOIN cutting_plans cp ON pp.plan_id = cp.id
           JOIN rough_stones rs ON cp.stone_id = rs.id
           LEFT JOIN workers w ON pp.worker_id = w.id
           WHERE pp.status = 'in_progress'
           ORDER BY pp.start_time"""
    )
    return {"status": "success", "count": len(rows), "processes": rows}


def get_process_history(plan_id: int) -> dict:
    """Get the full manufacturing history for a cutting plan.

    Args:
        plan_id: ID of the cutting plan.

    Returns:
        dict with all process steps for the plan.
    """
    rows = execute_read(
        """SELECT pp.*, w.name as worker_name
           FROM production_processes pp
           LEFT JOIN workers w ON pp.worker_id = w.id
           WHERE pp.plan_id = ?
           ORDER BY pp.id""",
        (plan_id,)
    )
    return {"status": "success", "plan_id": plan_id, "count": len(rows), "processes": rows}


def register_polished_diamond(
    stone_id: int,
    shape: str,
    weight_carat: float,
    color: str = "",
    clarity: str = "",
    cut_grade: str = "",
    fluorescence: str = "None",
    measurements: str = ""
) -> dict:
    """Register a finished polished diamond into the product inventory.

    Args:
        stone_id: ID of the original rough stone.
        shape: Final polished shape (e.g. 'Round Brilliant').
        weight_carat: Final polished weight in carats.
        color: Color grade (D-M) — can be set later during grading.
        clarity: Clarity grade (FL to I3) — can be set later during grading.
        cut_grade: Cut grade (Excellent to Poor) — can be set later.
        fluorescence: Fluorescence level (None, Faint, Medium, Strong).
        measurements: Dimensions string (e.g. '6.5x6.5x4.0mm').

    Returns:
        dict with the new polished diamond ID.
    """
    try:
        diamond_id = execute_query(
            """INSERT INTO polished_diamonds
               (stone_id, shape, weight_carat, color, clarity, cut_grade,
                fluorescence, measurements, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'available')""",
            (stone_id, shape, weight_carat, color, clarity, cut_grade,
             fluorescence, measurements)
        )

        # Update stone status
        execute_query("UPDATE rough_stones SET status = 'polished' WHERE id = ?", (stone_id,))

        # Mark cutting plan as completed
        execute_query(
            "UPDATE cutting_plans SET status = 'completed' WHERE stone_id = ?",
            (stone_id,)
        )

        return {
            "status": "success",
            "message": f"Polished diamond registered from stone {stone_id}.",
            "diamond_id": diamond_id,
            "shape": shape,
            "weight_carat": weight_carat
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
