"""
Sales Tools - Invoicing, pricing, and sales management.
Used by the Sales Agent for diamond sales operations.
"""

import random
from datetime import datetime
from diamond_erp.db import execute_query, execute_read, execute_read_one


def search_available_diamonds(
    shape: str = "",
    min_carat: float = 0,
    max_carat: float = 999,
    color_grade: str = "",
    clarity_grade: str = ""
) -> dict:
    """Search for polished diamonds available for sale.

    Args:
        shape: Filter by shape (e.g. 'Round Brilliant'). Empty for all shapes.
        min_carat: Minimum carat weight.
        max_carat: Maximum carat weight.
        color_grade: Filter by color grade (e.g. 'D', 'E'). Empty for all.
        clarity_grade: Filter by clarity grade (e.g. 'VS1'). Empty for all.

    Returns:
        dict with list of available diamonds matching criteria.
    """
    sql = """SELECT pd.*, rs.lot_id, rs.source, rs.purchase_price as rough_cost,
                    gr.certificate_number, gr.lab
             FROM polished_diamonds pd
             JOIN rough_stones rs ON pd.stone_id = rs.id
             LEFT JOIN grading_reports gr ON pd.id = gr.diamond_id
             WHERE pd.status IN ('available', 'graded', 'certified')
             AND pd.weight_carat BETWEEN ? AND ?"""
    params = [min_carat, max_carat]

    if shape:
        sql += " AND pd.shape LIKE ?"
        params.append(f"%{shape}%")
    if color_grade:
        sql += " AND pd.color = ?"
        params.append(color_grade)
    if clarity_grade:
        sql += " AND pd.clarity = ?"
        params.append(clarity_grade)

    sql += " ORDER BY pd.weight_carat DESC"
    rows = execute_read(sql, tuple(params))
    return {"status": "success", "count": len(rows), "diamonds": rows}


def calculate_price(
    diamond_id: int,
    price_per_carat: float
) -> dict:
    """Calculate the sale price for a diamond based on price per carat.

    Args:
        diamond_id: ID of the polished diamond.
        price_per_carat: Price per carat in USD.

    Returns:
        dict with price calculation details including profit margin.
    """
    diamond = execute_read_one(
        """SELECT pd.*, rs.purchase_price as rough_cost
           FROM polished_diamonds pd
           JOIN rough_stones rs ON pd.stone_id = rs.id
           WHERE pd.id = ?""",
        (diamond_id,)
    )
    if not diamond:
        return {"status": "error", "message": f"Diamond {diamond_id} not found."}

    total_price = round(diamond["weight_carat"] * price_per_carat, 2)
    rough_cost = diamond["rough_cost"] or 0
    profit = round(total_price - rough_cost, 2)
    margin = round((profit / total_price) * 100, 1) if total_price > 0 else 0

    return {
        "status": "success",
        "diamond_id": diamond_id,
        "carat_weight": diamond["weight_carat"],
        "price_per_carat": price_per_carat,
        "total_price": total_price,
        "rough_cost": rough_cost,
        "estimated_profit": profit,
        "profit_margin_pct": margin,
        "shape": diamond["shape"],
        "color": diamond["color"],
        "clarity": diamond["clarity"]
    }


def create_invoice(
    diamond_id: int,
    customer_name: str,
    sale_price: float,
    customer_email: str = "",
    customer_phone: str = "",
    payment_method: str = "wire_transfer",
    notes: str = ""
) -> dict:
    """Create a sales invoice for a polished diamond.

    Args:
        diamond_id: ID of the polished diamond being sold.
        customer_name: Full name or company name of the buyer.
        sale_price: Agreed sale price in USD.
        customer_email: Buyer's email address.
        customer_phone: Buyer's phone number.
        payment_method: Payment method (wire_transfer, check, cash, credit_card).
        notes: Additional invoice notes.

    Returns:
        dict with invoice number and sale details.
    """
    diamond = execute_read_one(
        """SELECT pd.*, rs.purchase_price as rough_cost
           FROM polished_diamonds pd
           JOIN rough_stones rs ON pd.stone_id = rs.id
           WHERE pd.id = ?""",
        (diamond_id,)
    )
    if not diamond:
        return {"status": "error", "message": f"Diamond {diamond_id} not found."}
    if diamond["status"] == "sold":
        return {"status": "error", "message": f"Diamond {diamond_id} is already sold."}

    invoice_number = f"INV-{datetime.now().year}-{random.randint(10000, 99999)}"
    cost_price = diamond["rough_cost"] or 0

    sale_id = execute_query(
        """INSERT INTO sales
           (diamond_id, customer_name, customer_email, customer_phone,
            sale_price, cost_price, sale_date, invoice_number,
            payment_status, payment_method, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
        (diamond_id, customer_name, customer_email, customer_phone,
         sale_price, cost_price, datetime.now().strftime("%Y-%m-%d"),
         invoice_number, payment_method, notes)
    )

    # Update diamond and stone status
    execute_query("UPDATE polished_diamonds SET status = 'sold' WHERE id = ?", (diamond_id,))
    execute_query(
        "UPDATE rough_stones SET status = 'sold' WHERE id = ?",
        (diamond["stone_id"],)
    )

    return {
        "status": "success",
        "message": f"Invoice created for diamond {diamond_id}.",
        "sale_id": sale_id,
        "invoice_number": invoice_number,
        "customer": customer_name,
        "sale_price": sale_price,
        "profit": round(sale_price - cost_price, 2)
    }


def record_payment(
    invoice_number: str,
    amount: float,
    payment_method: str = "wire_transfer"
) -> dict:
    """Record a payment received for an invoice.

    Args:
        invoice_number: The invoice number (e.g. 'INV-2026-12345').
        amount: Payment amount in USD.
        payment_method: Method of payment (wire_transfer, check, cash, credit_card).

    Returns:
        dict with payment confirmation.
    """
    sale = execute_read_one(
        "SELECT * FROM sales WHERE invoice_number = ?", (invoice_number,)
    )
    if not sale:
        return {"status": "error", "message": f"Invoice {invoice_number} not found."}
    if sale["payment_status"] == "paid":
        return {"status": "error", "message": f"Invoice {invoice_number} is already paid."}

    if amount >= sale["sale_price"]:
        payment_status = "paid"
    else:
        payment_status = "partial"

    execute_query(
        "UPDATE sales SET payment_status = ?, payment_method = ? WHERE invoice_number = ?",
        (payment_status, payment_method, invoice_number)
    )

    return {
        "status": "success",
        "message": f"Payment of ${amount:,.2f} recorded for invoice {invoice_number}.",
        "invoice_number": invoice_number,
        "payment_status": payment_status,
        "total_due": sale["sale_price"],
        "amount_paid": amount
    }


def get_sales_history(days: int = 30) -> dict:
    """Get recent sales history.

    Args:
        days: Number of days to look back. Default is 30.

    Returns:
        dict with recent sales records.
    """
    rows = execute_read(
        """SELECT s.*, pd.shape, pd.weight_carat, pd.color, pd.clarity
           FROM sales s
           JOIN polished_diamonds pd ON s.diamond_id = pd.id
           WHERE s.sale_date >= date('now', ?)
           ORDER BY s.sale_date DESC""",
        (f"-{days} days",)
    )

    total_revenue = sum(r["sale_price"] for r in rows)
    total_profit = sum((r["sale_price"] - (r["cost_price"] or 0)) for r in rows)

    return {
        "status": "success",
        "period_days": days,
        "count": len(rows),
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "sales": rows
    }
