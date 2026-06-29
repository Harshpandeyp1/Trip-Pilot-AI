from typing import List, Callable, Optional, Any

class Agent:
    """Simulated Agent class matching Google ADK."""
    def __init__(
        self,
        name: str,
        model: str,
        instruction: str = "",
        description: str = "",
        tools: Optional[List[Callable]] = None
    ):
        self.name = name
        self.model = model
        self.instruction = instruction
        self.description = description
        self.tools = tools or []

    def __repr__(self):
        return f"Agent(name={self.name}, model={self.model})"
