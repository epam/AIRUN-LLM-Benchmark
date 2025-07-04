from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union, Literal
import json
from enum import Enum

from anthropic.types import (
    TextBlockParam,
    ImageBlockParam,
    Base64ImageSourceParam,
    ToolUseBlockParam,
    ToolResultBlockParam,
)
from google.genai import types as genai_types
from openai.types.responses import (
    ResponseInputContentParam,
    ResponseInputTextParam,
    ResponseInputImageParam,
    ResponseFunctionToolCallParam,
    EasyInputMessageParam,
)
from openai.types.responses.response_input_param import FunctionCallOutput

from Utils.llm.ai_message import (
    AIMessage,
    TextAIMessageContent,
    ImageAIMessageContent,
    ToolCallAIMessageContent,
    ToolResponseAIMessageContent,
)


class MessageConverter(ABC):
    """Abstract base class for converting AIMessage objects to provider-specific formats."""

    @abstractmethod
    def convert(self, messages: List[AIMessage]) -> Any:
        """Convert list of AIMessage objects to provider-specific format."""
        pass


class OpenAICompletionsConverter(MessageConverter):
    """Converter for OpenAI Chat Completions API format."""

    def convert(self, messages: List[AIMessage]) -> List[Dict[str, Any]]:
        """Convert to OpenAI Chat Completions format with proper role handling."""
        api_messages = []

        for message in messages:
            # Handle different content types within a message
            text_content = []
            tool_calls = []

            for content in message.content:
                if isinstance(content, TextAIMessageContent):
                    text_content.append({"type": "text", "text": content.text})
                elif isinstance(content, ImageAIMessageContent):
                    text_content.extend(
                        [
                            {"type": "text", "text": f"Next image filename: {content.file_name}"},
                            {"type": "image_url", "image_url": {"url": content.to_base64_url()}},
                        ]
                    )
                elif isinstance(content, ToolCallAIMessageContent):
                    tool_calls.append(
                        {
                            "id": content.id,
                            "type": "function",
                            "function": {"name": content.name, "arguments": json.dumps(content.arguments)},
                        }
                    )
                elif isinstance(content, ToolResponseAIMessageContent):
                    # Tool responses get their own message with role "tool"
                    api_messages.append({"role": "tool", "content": content.result, "tool_call_id": content.id})
                    continue

            # Create message for text content and tool calls
            if text_content or tool_calls:
                msg = {"role": message.role, "content": text_content if text_content else []}
                if tool_calls:
                    msg["tool_calls"] = tool_calls
                api_messages.append(msg)

        return api_messages


class OpenAIResponsesConverter(MessageConverter):
    """Converter for OpenAI Responses API format."""

    def convert(
        self, messages: List[AIMessage]
    ) -> List[Union[EasyInputMessageParam, ResponseFunctionToolCallParam, FunctionCallOutput]]:
        """Convert to OpenAI Responses API format with mixed message types."""
        api_messages = []

        for message in messages:
            content_buffer = []
            role = "user" if message.role == "user" else "assistant"

            for content in message.content:
                if isinstance(content, TextAIMessageContent):
                    content_buffer.append(ResponseInputTextParam(type="input_text", text=content.text))
                elif isinstance(content, ImageAIMessageContent):
                    content_buffer.extend(
                        [
                            ResponseInputTextParam(type="input_text", text=f"Next image filename: {content.file_name}"),
                            ResponseInputImageParam(
                                type="input_image", image_url=content.to_base64_url(), detail="auto"
                            ),
                        ]
                    )
                elif isinstance(content, ToolCallAIMessageContent):
                    # Flush any buffered content before tool call
                    if content_buffer:
                        api_messages.append(EasyInputMessageParam(role=role, content=content_buffer))
                        content_buffer = []
                    
                    # Add tool call as separate item
                    api_messages.append(
                        ResponseFunctionToolCallParam(
                            type="function_call",
                            call_id=content.id,
                            name=content.name,
                            arguments=json.dumps(content.arguments),
                        )
                    )
                elif isinstance(content, ToolResponseAIMessageContent):
                    # Flush any buffered content before tool response
                    if content_buffer:
                        api_messages.append(EasyInputMessageParam(role=role, content=content_buffer))
                        content_buffer = []
                    
                    # Add tool response as separate item
                    api_messages.append(
                        FunctionCallOutput(type="function_call_output", call_id=content.id, output=content.result)
                    )

            # Flush any remaining buffered content
            if content_buffer:
                api_messages.append(EasyInputMessageParam(role=role, content=content_buffer))

        return api_messages


class AnthropicConverter(MessageConverter):
    """Converter for Anthropic API format."""

    def convert(self, messages: List[AIMessage]) -> List[Dict[str, Any]]:
        """Convert to Anthropic API format."""
        api_messages = []

        for message in messages:
            content = []

            for item in message.content:
                if isinstance(item, TextAIMessageContent):
                    content.append(TextBlockParam(type="text", text=item.text))
                elif isinstance(item, ImageAIMessageContent):
                    content.extend(
                        [
                            TextBlockParam(type="text", text=f"Next image file name: {item.file_name}"),
                            ImageBlockParam(
                                type="image",
                                source=Base64ImageSourceParam(
                                    type="base64", data=item.to_base64(), media_type=item.media_type()
                                ),
                            ),
                        ]
                    )
                elif isinstance(item, ToolCallAIMessageContent):
                    content.append(ToolUseBlockParam(type="tool_use", name=item.name, input=item.arguments, id=item.id))
                elif isinstance(item, ToolResponseAIMessageContent):
                    content.append(ToolResultBlockParam(type="tool_result", content=item.result, tool_use_id=item.id))

            api_messages.append({"role": message.role, "content": content})

        return api_messages


class GeminiConverter(MessageConverter):
    """Converter for Google Gemini API format."""

    def convert(self, messages: List[AIMessage]) -> List[genai_types.ContentDict]:
        """Convert to Gemini API format."""
        contents = []

        for message in messages:
            parts = []

            for content in message.content:
                if isinstance(content, TextAIMessageContent):
                    parts.append({"text": content.text})
                elif isinstance(content, ImageAIMessageContent):
                    parts.extend(
                        [
                            {"text": f"Next image file name: {content.file_name}"},
                            {"inline_data": {"data": content.binary_content, "mime_type": content.media_type()}},
                        ]
                    )
                elif isinstance(content, ToolCallAIMessageContent):
                    parts.append(genai_types.Part.from_function_call(name=content.name, args=content.arguments))
                elif isinstance(content, ToolResponseAIMessageContent):
                    parts.append(
                        genai_types.Part.from_function_response(name=content.name, response={"result": content.result})
                    )

            contents.append({"role": message.role, "parts": parts})

        return contents


class ConverterProvider(Enum):
    """Enumeration of available message converters."""

    OPENAI_COMPLETIONS = "openai_completions"
    OPENAI_RESPONSES = "openai_responses"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


def get_converter(provider: Union[ConverterProvider, str]) -> MessageConverter:
    """Factory function to get the appropriate message converter."""
    if isinstance(provider, str):
        try:
            provider = ConverterProvider(provider)
        except ValueError:
            raise ValueError(f"Unknown converter provider: {provider}")

    if provider == ConverterProvider.OPENAI_COMPLETIONS:
        return OpenAICompletionsConverter()
    elif provider == ConverterProvider.OPENAI_RESPONSES:
        return OpenAIResponsesConverter()
    elif provider == ConverterProvider.ANTHROPIC:
        return AnthropicConverter()
    elif provider == ConverterProvider.GEMINI:
        return GeminiConverter()
    else:
        raise ValueError(f"Unknown converter provider: {provider}")
