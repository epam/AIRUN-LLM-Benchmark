from dataclasses import dataclass, field
from typing import Optional, List

from Utils.llm.ai_message import AIMessage, AIMessageContent, ToolCallAIMessageContent


@dataclass
class LLMResponse:
    """Unified response from any LLM provider.

    Two audiences:
    - One-shot consumers (execute_test.py, auto_eval.py): use content, thoughts, tokens, error
    - Multi-turn consumers (instruction_following.py): use assistant_content to build AIMessage
    """

    # Core
    content: Optional[str]
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int = 0
    execute_time: float = 0.0
    error: Optional[str] = None

    # For display in reports (human-readable thinking/reasoning text)
    thoughts: Optional[str] = None

    # For multi-turn: full assistant message content in provider-correct order
    # (thinking blocks first, then tool calls, then text - whatever the provider needs)
    assistant_content: List[AIMessageContent] = field(default_factory=list)

    # Tool calls from response
    tool_calls: List[ToolCallAIMessageContent] = field(default_factory=list)

    def to_assistant_message(self, use_model_role: bool = False) -> AIMessage:
        """Build AIMessage from assistant_content for multi-turn conversations."""
        return AIMessage.create_assistant_message(self.assistant_content, use_model_role)