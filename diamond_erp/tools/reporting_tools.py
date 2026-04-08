"""
Reporting Tools - Analytics and ERP reports.
Used by the Reporting Agent for business intelligence and dashboards.
"""

from diamond_erp.db import execute_read, execute_read_one


def inventory_report() -> dict:
    """Generate a comprehensive inventory report showing stock levels across all stages.

    Returns:
        dict with inventory breakdown by status, recent acquisitions, and value analysis.
    """
    by_status = execute_read(
        """SELECT status, COUNT(*) as count,
                  ROUND(SUM(weight_carat), 2) as total_carats,
                  ROUND(SUM(purchase_price), 2) as total_value,
                  ROUND(AVG(weight_carat), 2) as avg_carat,
                  ROUND(AVG(purchase_price), 2) as avg_price
           FROM rough_stones GROUP BY status ORDER BY count DESC"""
    )

    by_source = execute_read(
        """SELECT source, COUNT(*) as count,
                  ROUND(SUM(weight_carat), 2) as total_carats,
                  ROUND(SUM(purchase_price), 2) as total_value
           FROM rough_stones GROUP BY source ORDER BY total_value DESC LIMIT 10"""
    )

    totals = execute_read_one(
        """SELECT COUNT(*) as total_stones,
                  ROUND(SUM(weight_carat), 2) as total_carats,
                  ROUND(SUM(purchase_price), 2) as total_invested,
                  ROUND(MIN(weight_carat), 2) as min_carat,
                  ROUND(MAX(weight_carat), 2) as max_carat
           FROM rough_stones"""
    )

    polished_summary = execute_read_one(
        """SELECT COUNT(*) as total_polished,
                  ROUND(SUM(weight_carat), 2) as total_polished_carats,
                  COUNT(CASE WHEN status = 'available' THEN 1 END) as available_count,
                  COUNT(CASE WHEN status = 'sold' THEN 1 END) as sold_count
           FROM polished_diamonds"""
    )

    return {
        "status": "success",
        "report_type": "Inventory Report",
        "rough_stones_by_status": by_status,
        "rough_stones_by_source": by_source,
        "totals": totals,
        "polished_summary": polished_summary
    }


def production_report(days: int = 30) -> dict:
    """Generate a production report showing manufacturing throughput and efficiency.

    Args:
        days: Number of days to look back. Default is 30.

    Returns:
        dict with production metrics including process counts, completion rates, and weight loss analysis.
    """
    process_summary = execute_read(
        """SELECT process_type,
                  COUNT(*) as total_processes,
                  COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                  COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
                  ROUND(AVG(CASE WHEN weight_before > 0 AND weight_after > 0
                            THEN ((weight_before - weight_after) / weight_before) * 100
                            END), 1) as avg_loss_pct
           FROM production_processes
           WHERE created_at >= date('now', ?)
           GROUP BY process_type""",
        (f"-{days} days",)
    )

    plan_summary = execute_read(
        """SELECT status, COUNT(*) as count
           FROM cutting_plans
           WHERE created_at >= date('now', ?)
           GROUP BY status""",
        (f"-{days} days",)
    )

    worker_output = execute_read(
        """SELECT w.name, w.role, COUNT(pp.id) as processes_completed,
                  ROUND(SUM(pp.weight_before - pp.weight_after), 2) as total_weight_processed
           FROM workers w
           LEFT JOIN production_processes pp ON w.id = pp.worker_id AND pp.status = 'completed'
           WHERE w.department = 'Production'
           GROUP BY w.id
           ORDER BY processes_completed DESC"""
    )

    return {
        "status": "success",
        "report_type": "Production Report",
        "period_days": days,
        "process_summary": process_summary,
        "plan_summary": plan_summary,
        "worker_output": worker_output
    }


def sales_report(days: int = 30) -> dict:
    """Generate a sales report with revenue analysis.

    Args:
        days: Number of days to look back. Default is 30.

    Returns:
        dict with sales metrics including revenue, profit, top customers, and popular shapes.
    """
    overview = execute_read_one(
        """SELECT COUNT(*) as total_sales,
                  ROUND(SUM(sale_price), 2) as total_revenue,
                  ROUND(SUM(sale_price - COALESCE(cost_price, 0)), 2) as total_profit,
                  ROUND(AVG(sale_price), 2) as avg_sale_price,
                  ROUND(MIN(sale_price), 2) as min_sale,
                  ROUND(MAX(sale_price), 2) as max_sale
           FROM sales
           WHERE sale_date >= date('now', ?)""",
        (f"-{days} days",)
    )

    by_customer = execute_read(
        """SELECT customer_name, COUNT(*) as purchases,
                  ROUND(SUM(sale_price), 2) as total_spent
           FROM sales
           WHERE sale_date >= date('now', ?)
           GROUP BY customer_name ORDER BY total_spent DESC""",
        (f"-{days} days",)
    )

    by_shape = execute_read(
        """SELECT pd.shape, COUNT(*) as sold,
                  ROUND(SUM(s.sale_price), 2) as revenue,
                  ROUND(AVG(s.sale_price / pd.weight_carat), 2) as avg_price_per_carat
           FROM sales s
           JOIN polished_diamonds pd ON s.diamond_id = pd.id
           WHERE s.sale_date >= date('now', ?)
           GROUP BY pd.shape ORDER BY revenue DESC""",
        (f"-{days} days",)
    )

    payment_status = execute_read(
        """SELECT payment_status, COUNT(*) as count,
                  ROUND(SUM(sale_price), 2) as total_amount
           FROM sales
           WHERE sale_date >= date('now', ?)
           GROUP BY payment_status""",
        (f"-{days} days",)
    )

    return {
        "status": "success",
        "report_type": "Sales Report",
        "period_days": days,
        "overview": overview,
        "by_customer": by_customer,
        "by_shape": by_shape,
        "payment_status": payment_status
    }


def profit_loss_report(days: int = 90) -> dict:
    """Generate a profit and loss analysis report.

    Args:
        days: Number of days to analyze. Default is 90.

    Returns:
        dict with P&L metrics including total investment, revenue, costs, and margins.
    """
    # Total investment in rough stones
    investment = execute_read_one(
        """SELECT ROUND(SUM(purchase_price), 2) as total_invested,
                  COUNT(*) as stones_purchased
           FROM rough_stones
           WHERE purchase_date >= date('now', ?)""",
        (f"-{days} days",)
    )

    # Revenue from sales
    revenue = execute_read_one(
        """SELECT ROUND(SUM(sale_price), 2) as total_revenue,
                  ROUND(SUM(cost_price), 2) as total_cost,
                  ROUND(SUM(sale_price - COALESCE(cost_price, 0)), 2) as gross_profit,
                  COUNT(*) as stones_sold
           FROM sales
           WHERE sale_date >= date('now', ?)""",
        (f"-{days} days",)
    )

    # Unsold inventory value
    unsold = execute_read_one(
        """SELECT COUNT(*) as unsold_count,
                  ROUND(SUM(rs.purchase_price), 2) as unsold_value
           FROM rough_stones rs
           WHERE rs.status NOT IN ('sold')"""
    )

    total_revenue = (revenue["total_revenue"] or 0) if revenue else 0
    total_cost = (revenue["total_cost"] or 0) if revenue else 0
    gross_profit = total_revenue - total_cost
    margin = round((gross_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0

    return {
        "status": "success",
        "report_type": "Profit & Loss Report",
        "period_days": days,
        "investment": investment,
        "revenue": revenue,
        "unsold_inventory": unsold,
        "summary": {
            "total_revenue": total_revenue,
            "total_cost_of_goods": total_cost,
            "gross_profit": gross_profit,
            "gross_margin_pct": margin
        }
    }


def worker_productivity(worker_id: int = 0) -> dict:
    """Get worker productivity metrics.

    Args:
        worker_id: Specific worker ID, or 0 for all workers.

    Returns:
        dict with worker performance metrics.
    """
    if worker_id > 0:
        workers = execute_read(
            """SELECT w.*, 
                      COUNT(pp.id) as total_processes,
                      COUNT(CASE WHEN pp.status = 'completed' THEN 1 END) as completed_processes,
                      ROUND(SUM(CASE WHEN pp.weight_before > 0 AND pp.weight_after > 0
                                THEN pp.weight_before - pp.weight_after END), 2) as total_weight_processed,
                      COUNT(DISTINCT cp.id) as plans_assigned
               FROM workers w
               LEFT JOIN production_processes pp ON w.id = pp.worker_id
               LEFT JOIN cutting_plans cp ON w.id = cp.assigned_worker_id
               WHERE w.id = ?
               GROUP BY w.id""",
            (worker_id,)
        )
    else:
        workers = execute_read(
            """SELECT w.*, 
                      COUNT(pp.id) as total_processes,
                      COUNT(CASE WHEN pp.status = 'completed' THEN 1 END) as completed_processes,
                      ROUND(SUM(CASE WHEN pp.weight_before > 0 AND pp.weight_after > 0
                                THEN pp.weight_before - pp.weight_after END), 2) as total_weight_processed,
                      COUNT(DISTINCT cp.id) as plans_assigned
               FROM workers w
               LEFT JOIN production_processes pp ON w.id = pp.worker_id
               LEFT JOIN cutting_plans cp ON w.id = cp.assigned_worker_id
               GROUP BY w.id
               ORDER BY completed_processes DESC"""
        )

    return {
        "status": "success",
        "report_type": "Worker Productivity",
        "count": len(workers),
        "workers": workers
    }
