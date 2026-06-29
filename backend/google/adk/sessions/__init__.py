class InMemorySessionService:
    """Simulated InMemorySessionService matching Google ADK."""
    def __init__(self):
        self.sessions = {}

    def get_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        return self.sessions[session_id]
