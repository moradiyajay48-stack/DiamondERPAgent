"""Grading Agent - Manages diamond grading and certification."""

from google.adk.agents import Agent
from diamond_erp.config import DEFAULT_MODEL
from diamond_erp.prompts import GRADING_AGENT_PROMPT
from diamond_erp.tools.grading_tools import (
    grade_diamond,
    get_grading_report,
    list_ungraded_diamonds,
    update_grading,
)

grading_agent = Agent(
    name="grading_agent",
    model=DEFAULT_MODEL,
    description="Performs GIA-style diamond grading (4Cs), generates certificates, and manages quality reports.",
    instruction=GRADING_AGENT_PROMPT,
    tools=[
        grade_diamond,
        get_grading_report,
        list_ungraded_diamonds,
        update_grading,
    ],
)
