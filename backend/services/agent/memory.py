import uuid
from typing import List, Dict, Any, Optional

class ConversationTurn:
    def __init__(self, query: str, response: str, tools_used: List[str]):
        self.query = query
        self.response = response
        self.tools_used = tools_used

class ConversationContext:
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.turns: List[ConversationTurn] = []

    def add_turn(self, query: str, response: str, tools_used: List[str]):
        self.turns.append(ConversationTurn(query, response, tools_used))
        # Keep last 10 turns to avoid memory growth
        if len(self.turns) > 10:
            self.turns = self.turns[-10:]

    def get_last_queries(self, count: int = 3) -> List[str]:
        return [turn.query for turn in self.turns[-count:]]

    def get_last_responses(self, count: int = 3) -> List[str]:
        return [turn.response for turn in self.turns[-count:]]

    def get_tool_usage(self) -> List[str]:
        tools = []
        for turn in self.turns:
            tools.extend(turn.tools_used)
        return list(set(tools))

    def format_history_context(self, max_turns: int = 3) -> str:
        if not self.turns:
            return ""
        recent = self.turns[-max_turns:]
        formatted = []
        for t in recent:
            formatted.append(f"User: {t.query}\nAssistant: {t.response}")
        return "\n\n".join(formatted)


class AgentMemoryManager:
    """
    In-memory lightweight conversation context store keyed by conversation_id.
    """
    def __init__(self):
        self._conversations: Dict[str, ConversationContext] = {}

    def get_or_create(self, conversation_id: Optional[str] = None) -> ConversationContext:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = ConversationContext(conversation_id)
        return self._conversations[conversation_id]

    def add_interaction(self, conversation_id: str, query: str, response: str, tools_used: List[str]):
        ctx = self.get_or_create(conversation_id)
        ctx.add_turn(query, response, tools_used)

# Global singleton memory instance
agent_memory = AgentMemoryManager()
