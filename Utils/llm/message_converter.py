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
    ThinkingBlockParam,
    RedactedThinkingBlockParam,
)
from google.genai import types as genai_types
from openai.types.responses import (
    ResponseInputTextParam,
    ResponseInputImageParam,
    ResponseFunctionToolCallParam,
    EasyInputMessageParam,
    ResponseOutputTextParam,
    ResponseReasoningItemParam,
)
from openai.types.responses.response_input_param import FunctionCallOutput

from Utils.llm.ai_message import (
    AIMessage,
    TextAIMessageContent,
    ImageAIMessageContent,
    ToolCallAIMessageContent,
    ToolResponseAIMessageContent,
    ThinkingAIMessageContent,
    RedactedThinkingAIMessageContent,
    ReasoningAIMessageContent,
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
                msg = {"role": message.role, "content": text_content or None}
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
                if isinstance(content, ReasoningAIMessageContent):
                    # Flush buffer before reasoning item
                    if content_buffer:
                        api_messages.append(EasyInputMessageParam(role=role, content=content_buffer))
                        content_buffer = []
                    reasoning_param = ResponseReasoningItemParam(
                        type="reasoning",
                        id=content.reasoning_id,
                        summary=content.summary,
                        encrypted_content=content.encrypted_content,
                    )
                    api_messages.append(reasoning_param)
                elif isinstance(content, TextAIMessageContent):
                    if role == "assistant":
                        content_buffer.append(ResponseOutputTextParam(type="output_text", text=content.text, annotations=[]))
                    else:
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
                    tool_call_param = ResponseFunctionToolCallParam(
                        type="function_call",
                        call_id=content.id,
                        name=content.name,
                        arguments=json.dumps(content.arguments),
                    )
                    if content.item_id:
                        tool_call_param["id"] = content.item_id
                    api_messages.append(tool_call_param)
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
                elif isinstance(item, ThinkingAIMessageContent):
                    # Preserve thinking blocks with signature for multi-turn conversations
                    thinking_param = ThinkingBlockParam(type="thinking", thinking=item.thinking)
                    if item.signature:
                        thinking_param["signature"] = item.signature
                    content.append(thinking_param)
                elif isinstance(item, RedactedThinkingAIMessageContent):
                    # Preserve redacted thinking blocks for multi-turn conversations
                    content.append(RedactedThinkingBlockParam(type="redacted_thinking", data=item.data))

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
                if isinstance(content, ThinkingAIMessageContent):
                    # Gemini thinking part - must be returned in multi-turn
                    thought_part = genai_types.Part(text=content.thinking, thought=True)
                    if content.signature:
                        thought_part.thought_signature = content.signature
                    parts.append(thought_part)
                elif isinstance(content, TextAIMessageContent):
                    parts.append({"text": content.text})
                elif isinstance(content, ImageAIMessageContent):
                    parts.extend(
                        [
                            {"text": f"Next image file name: {content.file_name}"},
                            {"inline_data": {"data": content.binary_content, "mime_type": content.media_type()}},
                        ]
                    )
                elif isinstance(content, ToolCallAIMessageContent):
                    part = genai_types.Part.from_function_call(name=content.name, args=content.arguments)
                    # Add thought_signature if present
                    if content.signature:
                        part.thought_signature = content.signature
                    parts.append(part)
                elif isinstance(content, ToolResponseAIMessageContent):
                    parts.append(
                        genai_types.Part.from_function_response(name=content.name, response={"result": content.result})
                    )

            contents.append({"role": message.role, "parts": parts})

        return contents


class AmazonNovaConverter(MessageConverter):
    """Converter for Amazon Nova API format."""

    def convert(self, messages: List[AIMessage]) -> List[Dict[str, Any]]:
        """Convert to Amazon Nova API format."""
        formatted_messages = []

        for message in messages:
            api_content = []

            for content in message.content:
                if isinstance(content, TextAIMessageContent):
                    api_content.append({"text": content.text})
                elif isinstance(content, ImageAIMessageContent):
                    api_content.append({"text": f"Next image file name: {content.file_name}"})
                    api_content.append(
                        {
                            "image": {
                                "format": content.media_type().split("/")[1],
                                "source": {"bytes": content.binary_content},
                            }
                        }
                    )
                elif isinstance(content, ToolCallAIMessageContent):
                    api_content.append(
                        {"toolUse": {"toolUseId": content.id, "name": content.name, "input": content.arguments}}
                    )
                elif isinstance(content, ToolResponseAIMessageContent):
                    api_content.append(
                        {
                            "toolResult": {
                                "toolUseId": content.id,
                                "content": [{"text": content.result}],
                                "status": "success",
                            }
                        }
                    )

            formatted_messages.append({"role": message.role, "content": api_content})

        return formatted_messages


class ConverterProvider(Enum):
    """Enumeration of available message converters."""

    OPENAI_COMPLETIONS = "openai_completions"
    OPENAI_RESPONSES = "openai_responses"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    AMAZON_NOVA = "amazon_nova"


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
    elif provider == ConverterProvider.AMAZON_NOVA:
        return AmazonNovaConverter()
    else:
        raise ValueError(f"Unknown converter provider: {provider}")
