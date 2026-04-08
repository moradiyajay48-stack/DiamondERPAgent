"""
Grading Tools - Diamond grading and certification.
Used by the Grading Agent to manage GIA-style grading processes.
"""

import random
from datetime import datetime
from diamond_erp.db import execute_query, execute_read, execute_read_one


def grade_diamond(
    diamond_id: int,
    color_grade: str,
    clarity_grade: str,
    cut_grade: str,
    grader: str,
    polish: str = "Very Good",
    symmetry: str = "Very Good",
    fluorescence: str = "None",
    lab: str = "GIA",
    notes: str = ""
) -> dict:
    """Submit a grading report for a polished diamond.

    Args:
        diamond_id: ID of the polished diamond.
        color_grade: Color grade (D, E, F, G, H, I, J, K, L, M).
        clarity_grade: Clarity grade (FL, IF, VVS1, VVS2, VS1, VS2, SI1, SI2, I1, I2, I3).
        cut_grade: Cut grade (Excellent, Very Good, Good, Fair, Poor).
        grader: Name of the person grading.
        polish: Polish quality (Excellent, Very Good, Good, Fair, Poor).
        symmetry: Symmetry quality (Excellent, Very Good, Good, Fair, Poor).
        fluorescence: Fluorescence (None, Faint, Medium, Strong, Very Strong).
        lab: Grading lab (GIA, IGI, HRD, AGS).
        notes: Additional grading notes.

    Returns:
        dict with grading report details and certificate number.
    """
    diamond = execute_read_one(
        "SELECT * FROM polished_diamonds WHERE id = ?", (diamond_id,)
    )
    if not diamond:
        return {"status": "error", "message": f"Diamond {diamond_id} not found."}

    # Check if already graded
    existing = execute_read_one(
        "SELECT * FROM grading_reports WHERE diamond_id = ?", (diamond_id,)
    )
    if existing:
        return {"status": "error", "message": f"Diamond {diamond_id} already has a grading report (cert: {existing['certificate_number']})."}

    # Generate certificate number
    cert_number = f"{lab}-{random.randint(100000000, 999999999)}"

    report_id = execute_query(
        """INSERT INTO grading_reports
           (diamond_id, grader, grade_date, color_grade, clarity_grade, cut_grade,
            carat_weight, certificate_number, lab, polish, symmetry, fluorescence, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (diamond_id, grader, datetime.now().strftime("%Y-%m-%d"),
         color_grade, clarity_grade, cut_grade, diamond["weight_carat"],
         cert_number, lab, polish, symmetry, fluorescence, notes)
    )

    # Update diamond with grading info
    execute_query(
        """UPDATE polished_diamonds
           SET color = ?, clarity = ?, cut_grade = ?, fluorescence = ?, status = 'graded'
           WHERE id = ?""",
        (color_grade, clarity_grade, cut_grade, fluorescence, diamond_id)
    )

    # Update original rough stone status
    execute_query(
        "UPDATE rough_stones SET status = 'graded' WHERE id = ?",
        (diamond["stone_id"],)
    )

    return {
        "status": "success",
        "message": f"Diamond {diamond_id} graded successfully.",
        "report_id": report_id,
        "certificate_number": cert_number,
        "lab": lab,
        "grades": {
            "color": color_grade,
            "clarity": clarity_grade,
            "cut": cut_grade,
            "polish": polish,
            "symmetry": symmetry,
            "carat": diamond["weight_carat"]
        }
    }


def get_grading_report(diamond_id: int) -> dict:
    """Retrieve the full grading report for a polished diamond.

    Args:
        diamond_id: ID of the polished diamond.

    Returns:
        dict with the complete grading report.
    """
    report = execute_read_one(
        """SELECT gr.*, pd.shape, pd.measurements, pd.weight_carat as polished_weight,
                  rs.lot_id, rs.source
           FROM grading_reports gr
           JOIN polished_diamonds pd ON gr.diamond_id = pd.id
           JOIN rough_stones rs ON pd.stone_id = rs.id
           WHERE gr.diamond_id = ?""",
        (diamond_id,)
    )
    if not report:
        return {"status": "error", "message": f"No grading report found for diamond {diamond_id}."}

    return {"status": "success", "report": report}


def list_ungraded_diamonds() -> dict:
    """Find all polished diamonds that haven't been graded yet.

    Returns:
        dict with list of polished diamonds needing grading.
    """
    rows = execute_read(
        """SELECT pd.*, rs.lot_id, rs.source
           FROM polished_diamonds pd
           JOIN rough_stones rs ON pd.stone_id = rs.id
           LEFT JOIN grading_reports gr ON pd.id = gr.diamond_id
           WHERE gr.id IS NULL
           ORDER BY pd.weight_carat DESC"""
    )
    return {"status": "success", "count": len(rows), "diamonds": rows}


def update_grading(
    diamond_id: int,
    color_grade: str = "",
    clarity_grade: str = "",
    cut_grade: str = ""
) -> dict:
    """Update an existing grading report (for corrections).

    Args:
        diamond_id: ID of the polished diamond.
        color_grade: Updated color grade (leave empty to keep current).
        clarity_grade: Updated clarity grade (leave empty to keep current).
        cut_grade: Updated cut grade (leave empty to keep current).

    Returns:
        dict with update confirmation.
    """
    report = execute_read_one(
        "SELECT * FROM grading_reports WHERE diamond_id = ?", (diamond_id,)
    )
    if not report:
        return {"status": "error", "message": f"No grading report for diamond {diamond_id}."}

    updates = []
    params = []
    if color_grade:
        updates.append("color_grade = ?")
        params.append(color_grade)
    if clarity_grade:
        updates.append("clarity_grade = ?")
        params.append(clarity_grade)
    if cut_grade:
        updates.append("cut_grade = ?")
        params.append(cut_grade)

    if not updates:
        return {"status": "error", "message": "No updates provided."}

    params.append(diamond_id)
    execute_query(
        f"UPDATE grading_reports SET {', '.join(updates)} WHERE diamond_id = ?",
        tuple(params)
    )

    # Also update polished_diamonds table
    pd_updates = []
    pd_params = []
    if color_grade:
        pd_updates.append("color = ?")
        pd_params.append(color_grade)
    if clarity_grade:
        pd_updates.append("clarity = ?")
        pd_params.append(clarity_grade)
    if cut_grade:
        pd_updates.append("cut_grade = ?")
        pd_params.append(cut_grade)
    pd_params.append(diamond_id)
    execute_query(
        f"UPDATE polished_diamonds SET {', '.join(pd_updates)} WHERE id = ?",
        tuple(pd_params)
    )

    return {"status": "success", "message": f"Grading for diamond {diamond_id} updated."}
