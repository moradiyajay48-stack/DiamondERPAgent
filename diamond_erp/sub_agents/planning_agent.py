"""Planning Agent - Manages cutting plans and yield estimation."""

from google.adk.agents import Agent
from diamond_erp.config import DEFAULT_MODEL
from diamond_erp.prompts import PLANNING_AGENT_PROMPT
from diamond_erp.tools.planning_tools import (
    create_cutting_plan,
    get_pending_plans,
    estimate_yield,
    assign_worker,
    get_all_plans,
)

planning_agent = Agent(
    name="planning_agent",
    model=DEFAULT_MODEL,
    description="Creates cutting plans, estimates polished diamond yield, and assigns workers for manufacturing.",
    instruction=PLANNING_AGENT_PROMPT,
    tools=[
        create_cutting_plan,
        get_pending_plans,
        estimate_yield,
        assign_worker,
        get_all_plans,
    ],
)
