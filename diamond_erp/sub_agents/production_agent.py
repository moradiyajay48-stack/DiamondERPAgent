"""Production Agent - Manages manufacturing processes."""

from google.adk.agents import Agent
from diamond_erp.config import DEFAULT_MODEL
from diamond_erp.prompts import PRODUCTION_AGENT_PROMPT
from diamond_erp.tools.production_tools import (
    start_process,
    complete_process,
    get_active_processes,
    get_process_history,
    register_polished_diamond,
)

production_agent = Agent(
    name="production_agent",
    model=DEFAULT_MODEL,
    description="Tracks manufacturing processes (sawing, bruting, cutting, polishing), weight loss, and registers finished polished diamonds.",
    instruction=PRODUCTION_AGENT_PROMPT,
    tools=[
        start_process,
        complete_process,
        get_active_processes,
        get_process_history,
        register_polished_diamond,
    ],
)
