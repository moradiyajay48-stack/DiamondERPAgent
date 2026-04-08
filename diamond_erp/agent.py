"""
Diamond ERP Root Orchestrator Agent
Central coordinator that delegates to specialized sub-agents.
"""

from google.adk.agents import Agent
from diamond_erp.config import DEFAULT_MODEL
from diamond_erp.prompts import ORCHESTRATOR_PROMPT

from diamond_erp.sub_agents.inventory_agent import inventory_agent
from diamond_erp.sub_agents.planning_agent import planning_agent
from diamond_erp.sub_agents.production_agent import production_agent
from diamond_erp.sub_agents.grading_agent import grading_agent
from diamond_erp.sub_agents.sales_agent import sales_agent
from diamond_erp.sub_agents.reporting_agent import reporting_agent


root_agent = Agent(
    name="diamond_erp_orchestrator",
    model=DEFAULT_MODEL,
    description="Diamond Manufacturing ERP Orchestrator — coordinates inventory, planning, production, grading, sales, and reporting agents.",
    instruction=ORCHESTRATOR_PROMPT,
    sub_agents=[
        inventory_agent,
        planning_agent,
        production_agent,
        grading_agent,
        sales_agent,
        reporting_agent,
    ],
)
