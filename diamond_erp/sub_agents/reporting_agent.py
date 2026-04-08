"""Reporting Agent - Business analytics and reports."""

from google.adk.agents import Agent
from diamond_erp.config import DEFAULT_MODEL
from diamond_erp.prompts import REPORTING_AGENT_PROMPT
from diamond_erp.tools.reporting_tools import (
    inventory_report,
    production_report,
    sales_report,
    profit_loss_report,
    worker_productivity,
)

reporting_agent = Agent(
    name="reporting_agent",
    model=DEFAULT_MODEL,
    description="Generates business reports — inventory, production, sales, P&L analysis, and worker productivity.",
    instruction=REPORTING_AGENT_PROMPT,
    tools=[
        inventory_report,
        production_report,
        sales_report,
        profit_loss_report,
        worker_productivity,
    ],
)
