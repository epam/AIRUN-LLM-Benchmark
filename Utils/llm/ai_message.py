import base64
import json
from typing import Literal, List, Dict, Union, Sequence
from abc import ABC, abstractmethod

MediaType = Literal["image/jpeg", "image/png", "image/gif"]


class AIMessageContent(ABC):
    """Abstract base class for all AI message content types"""

    @abstractmethod
    def __str__(self) -> str:
        pass


class AIMessageContentFactory:
    """Factory for creating different types of AI message content"""

    @staticmethod
    def create_text(text: str) -> "TextAIMessageContent":
        """Create a text message content"""
        return TextAIMessageContent(text)

    @staticmethod
    def create_tool_call(name: str, arguments: dict, tool_id: str, signature: Union[bytes, None] = None, item_id: Union[str, None] = None) -> "ToolCallAIMessageContent":
        """Create a tool call message content"""
        return ToolCallAIMessageContent(name, arguments, tool_id, signature, item_id)

    @staticmethod
    def create_tool_response(name: str, result: str, tool_id: str) -> "ToolResponseAIMessageContent":
        """Create a tool response message content"""
        return ToolResponseAIMessageContent(name, result, tool_id)

    @staticmethod
    def create_image(file_name: str, binary_content: bytes) -> "ImageAIMessageContent":
        """Create an image message content"""
        return ImageAIMessageContent(file_name, binary_content)

    @staticmethod
    def create_thinking(thinking: str, signature: Union[str, None] = None) -> "ThinkingAIMessageContent":
        """Create a thinking message content"""
        return ThinkingAIMessageContent(thinking, signature)

    @staticmethod
    def create_redacted_thinking(data: str) -> "RedactedThinkingAIMessageContent":
        """Create a redacted thinking message content"""
        return RedactedThinkingAIMessageContent(data)

    @staticmethod
    def create_reasoning(reasoning_id: str, summary: List[Dict[str, str]], encrypted_content: str) -> "ReasoningAIMessageContent":
        """Create a reasoning message content (OpenAI Responses API)."""
        return ReasoningAIMessageContent(reasoning_id, summary, encrypted_content)


class TextAIMessageContent(AIMessageContent):
    text: str

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def __str__(self):
        return self.text


class ImageAIMessageContent(AIMessageContent):
    file_name: str
    binary_content: bytes
    SUPPORTED_FORMATS: dict[str, MediaType] = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
    }

    def __init__(
        self,
        file_name: str,
        binary_content: bytes,
    ):
        super().__init__()
        self.file_name = file_name
        self.binary_content = binary_content

    def media_type(self) -> MediaType:
        file_extension = self.file_name.split(".")[-1].lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported image format: {file_extension}")

        return self.SUPPORTED_FORMATS[file_extension]

    def to_base64(self) -> str:
        return base64.b64encode(self.binary_content).decode("utf-8")

    def to_base64_url(self) -> str:
        return f"data:{self.media_type()};base64,{self.to_base64()}"

    def __str__(self):
        return f"[image: {self.file_name}]"


class ToolCallAIMessageContent(AIMessageContent):
    name: str
    arguments: dict
    id: str
    signature: Union[bytes, None]
    item_id: Union[str, None]  # OpenAI Responses API function_call id (fc_...)

    def __init__(self, name: str, arguments: dict, id: str, signature: Union[bytes, None] = None, item_id: Union[str, None] = None):
        super().__init__()
        self.name = name
        self.arguments = arguments
        self.id = id
        self.signature = signature
        self.item_id = item_id

    def __str__(self):
        result = {"name": self.name, "arguments": self.arguments, "id": self.id}
        if self.signature:
            # bytes are not JSON serializable, so represent them as a placeholder
            result["signature"] = "<bytes>"
        return json.dumps(result)


class ToolResponseAIMessageContent(AIMessageContent):
    name: str
    result: str
    id: str

    def __init__(self, name: str, result: str, id: str):
        super().__init__()
        self.name = name
        self.result = result
        self.id = id

    def __str__(self):
        return json.dumps({"name": self.name, "result": self.result, "id": self.id})


class ThinkingAIMessageContent(AIMessageContent):
    """Thinking block from Claude models (regular thinking)"""

    thinking: str
    signature: Union[str, None]

    def __init__(self, thinking: str, signature: Union[str, None] = None):
        super().__init__()
        self.thinking = thinking
        self.signature = signature

    def __str__(self):
        return f"[THINKING]: {self.thinking}"


class RedactedThinkingAIMessageContent(AIMessageContent):
    """Redacted thinking block from Claude models (encrypted for safety)"""

    data: str

    def __init__(self, data: str):
        super().__init__()
        self.data = data

    def __str__(self):
        return f"[REDACTED THINKING - {len(self.data)} bytes]"


class ReasoningAIMessageContent(AIMessageContent):
    """Reasoning item from OpenAI Responses API.

    Stores only the fields needed for multi-turn: id, summary, encrypted_content.
    See: https://platform.openai.com/docs/guides/reasoning
    """

    reasoning_id: str
    summary: List[Dict[str, str]]
    encrypted_content: str

    def __init__(self, reasoning_id: str, summary: List[Dict[str, str]], encrypted_content: str):
        super().__init__()
        self.reasoning_id = reasoning_id
        self.summary = summary
        self.encrypted_content = encrypted_content

    def __str__(self):
        texts = [s.get("text", "") for s in self.summary]
        return f"[REASONING]: {' '.join(texts)}"


class AIMessage:
    """AI Message with proper type safety and factory pattern support"""

    def __init__(self, role: str, content: List[AIMessageContent]):
        self.role = role
        self.content = content

    @classmethod
    def create_user_message(cls, content: Union[str, Sequence[AIMessageContent]]) -> "AIMessage":
        """Factory method to create user messages"""
        if isinstance(content, str):
            return cls("user", [AIMessageContentFactory.create_text(content)])
        return cls("user", list(content))

    @classmethod
    def create_assistant_message(
        cls, content: Union[str, Sequence[AIMessageContent]], use_model_role: bool = False
    ) -> "AIMessage":
        """Factory method to create assistant messages"""
        role = "model" if use_model_role else "assistant"
        if isinstance(content, str):
            return cls(role, [AIMessageContentFactory.create_text(content)])
        return cls(role, list(content))

    def __str__(self):
        return json.dumps({"role": self.role, "content": [c.__str__() for c in self.content]}, indent=4)
