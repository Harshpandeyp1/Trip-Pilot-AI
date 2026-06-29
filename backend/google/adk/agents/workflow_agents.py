from typing import List, Any

class SequentialAgent:
    """Simulated SequentialAgent workflow matching Google ADK."""
    def __init__(self, name: str, sub_agents: List[Any]):
        self.name = name
        self.sub_agents = sub_agents

    def __repr__(self):
        return f"SequentialAgent(name={self.name}, sub_agents_count={len(self.sub_agents)})"
