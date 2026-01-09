REQUIRED_FIELDS = {
    "category": ["hardware", "software"],
    "affected_system": None,
    "impact": None,
    "urgency": ["low", "medium", "high", "critical"],
}
class HostConversationState:
    def __init__(self):
        self.sessions = {}

    def get(self, context_id):
        return self.sessions.setdefault(context_id, {})

    def update(self, context_id, updates: dict):
        state = self.get(context_id)
        state.update(updates)
        return state

    def clear(self, context_id):
        self.sessions.pop(context_id, None)
