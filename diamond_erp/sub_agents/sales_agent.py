"""Sales Agent - Manages diamond sales and invoicing."""

from google.adk.agents import Agent
from diamond_erp.config import DEFAULT_MODEL
from diamond_erp.prompts import SALES_AGENT_PROMPT
from diamond_erp.tools.sales_tools import (
    search_available_diamonds,
    calculate_price,
    create_invoice,
    record_payment,
    get_sales_history,
)

sales_agent = Agent(
    name="sales_agent",
    model=DEFAULT_MODEL,
    description="Handles diamond pricing, customer sales, invoicing, and payment tracking.",
    instruction=SALES_AGENT_PROMPT,
    tools=[
        search_available_diamonds,
        calculate_price,
        create_invoice,
        record_payment,
        get_sales_history,
    ],
)
