from typing import Dict, List, Any, Optional, cast
from enum import Enum

from anthropic.types import ToolParam as AnthropicToolParam
from openai.types.responses import FunctionToolParam as OpenAIResponsesToolParam
from openai.types.chat import ChatCompletionToolParam as OpenAIToolParam
from google.genai import types


class ToolProvider(Enum):
    OPENAI_RESPONSES = "openai_responses"
    OPENAI_COMPLETIONS = "openai_completions"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class AIToolParameter:
    def __init__(
        self,
        name: str,
        param_type: str,
        description: str,
        required: bool = False,
        enum_values: Optional[List[str]] = None,
        items_type: Optional[str] = None,
    ):
        self.name = name
        self.param_type = param_type
        self.description = description
        self.required = required
        self.enum_values = enum_values
        self.items_type = items_type

    def to_schema_property(self) -> Dict[str, Any]:
        """Convert to JSON schema property format"""
        prop: Dict[str, Any] = {"type": self.param_type, "description": self.description}

        if self.enum_values:
            prop["enum"] = self.enum_values

        if self.param_type == "array" and self.items_type:
            prop["items"] = {"type": self.items_type}

        return prop


class AITool:
    def __init__(self, name: str, description: str, parameters: Optional[List[AIToolParameter]] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or []

    # def add_parameter(self, parameter: AIToolParameter) -> 'AITool':
    #     """Add a parameter to the tool"""
    #     self.parameters.append(parameter)
    #     return self

    def to_anthropic_format(self) -> AnthropicToolParam:
        """Convert to Anthropic/Claude tool format"""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema_property()
            if param.required:
                required.append(param.name)

        return AnthropicToolParam(
            name=self.name,
            description=self.description,
            input_schema={"type": "object", "properties": properties, "required": required},
        )

    def to_openai_responses_format(self) -> OpenAIResponsesToolParam:
        """Convert to OpenAI tool format"""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema_property()
            if param.required:
                required.append(param.name)

        return OpenAIResponsesToolParam(
            name=self.name,
            type="function",
            description=self.description,
            strict=True,
            parameters={
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        )

    def to_openai_completions_format(self) -> OpenAIToolParam:
        """Convert to OpenAI Chat Completions tool format"""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema_property()
            if param.required:
                required.append(param.name)

        return OpenAIToolParam(
            type="function",
            function={
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
            },
        )

    def to_gemini_format(self) -> types.FunctionDeclaration:
        """Convert to Gemini tool format"""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema_property()
            if param.required:
                required.append(param.name)

        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema(type=types.Type.OBJECT, properties=properties, required=required),
        )

    def __str__(self) -> str:
        return f"AITool(name='{self.name}', parameters={len(self.parameters)})"

    def __repr__(self) -> str:
        return self.__str__()


class AIToolSet:
    """Collection of AI tools with bulk conversion methods"""

    def __init__(self, tools: Optional[List[AITool]] = None):
        self.tools = tools or []

    def add_tool(self, tool: AITool) -> "AIToolSet":
        """Add a tool to the set"""
        self.tools.append(tool)
        return self

    def to_format(self, provider: ToolProvider):
        """Convert all tools to specified provider format"""
        if provider == ToolProvider.ANTHROPIC:
            return [tool.to_anthropic_format() for tool in self.tools]
        elif provider == ToolProvider.OPENAI_RESPONSES:
            return [tool.to_openai_responses_format() for tool in self.tools]
        elif provider == ToolProvider.OPENAI_COMPLETIONS:
            return [tool.to_openai_completions_format() for tool in self.tools]
        elif provider == ToolProvider.GEMINI:
            return [types.Tool(function_declarations=[tool.to_gemini_format() for tool in self.tools])]
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def to_anthropic_format(self) -> List[AnthropicToolParam]:
        """Convert all tools to Anthropic format"""
        return cast(List[AnthropicToolParam], self.to_format(ToolProvider.ANTHROPIC))

    def to_openai_responses_format(self) -> List[OpenAIResponsesToolParam]:
        """Convert all tools to OpenAI Responses format"""
        return cast(List[OpenAIResponsesToolParam], self.to_format(ToolProvider.OPENAI_RESPONSES))

    def to_openai_completions_format(self) -> List[OpenAIToolParam]:
        """Convert all tools to OpenAI Chat Completions format"""
        return cast(List[OpenAIToolParam], self.to_format(ToolProvider.OPENAI_COMPLETIONS))

    def to_gemini_format(self) -> List[types.Tool]:
        """Convert all tools to Gemini format"""
        return cast(List[types.Tool], self.to_format(ToolProvider.GEMINI))

    def __len__(self) -> int:
        return len(self.tools)

    def __iter__(self):
        return iter(self.tools)

    def __getitem__(self, index):
        return self.tools[index]
