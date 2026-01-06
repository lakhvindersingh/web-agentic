"""Agent state definition."""
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Agent state definition."""
    messages: Annotated[list, add_messages]
    step_count: int
    max_steps: int

