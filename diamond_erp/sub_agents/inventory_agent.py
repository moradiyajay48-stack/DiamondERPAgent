"""Inventory Agent - Manages rough diamond stone inventory."""

from google.adk.agents import Agent
from diamond_erp.config import DEFAULT_MODEL
from diamond_erp.prompts import INVENTORY_AGENT_PROMPT
from diamond_erp.tools.inventory_tools import (
    add_rough_stone,
    get_inventory_summary,
    search_stones,
    get_stone_details,
    update_stone_status,
)

inventory_agent = Agent(
    name="inventory_agent",
    model=DEFAULT_MODEL,
    description="Manages rough diamond stone inventory — intake, stock queries, tracking, and status updates.",
    instruction=INVENTORY_AGENT_PROMPT,
    tools=[
        add_rough_stone,
        get_inventory_summary,
        search_stones,
        get_stone_details,
        update_stone_status,
    ],
)
