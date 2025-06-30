from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Any, Dict, Union
from anthropic.types import TextBlockParam, ImageBlockParam, Base64ImageSourceParam, ToolUseBlockParam, ToolResultBlockParam
from google.genai import types as genai_types
from openai.types.responses import (
    ResponseInputContentParam, 
    ResponseInputTextParam, 
    ResponseInputImageParam,
    ResponseFunctionToolCallParam,
)
from openai.types.responses.response_input_param import FunctionCallOutput

from Utils.llm.ai_message import AIMessageContent, TextAIMessageContent, ImageAIMessageContent, ToolCallAIMessageContent, ToolResponseAIMessageContent


class FormatterProvider(Enum):
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENAI_RESPONSES = "openai_responses"
    OPENAI = "openai"


class MessageContentFormatter(ABC):
    @abstractmethod
    def format(self, content: AIMessageContent) -> List[Any]:
        pass


# Anthropic formatters
class AnthropicTextMessageFormatter(MessageContentFormatter):
    def format(self, content: TextAIMessageContent) -> List[TextBlockParam]:
        return [TextBlockParam(text=content.text, type="text")]


class AnthropicImageMessageFormatter(MessageContentFormatter):
    def format(self, content: ImageAIMessageContent) -> List[Union[TextBlockParam, ImageBlockParam]]:
        return [
            TextBlockParam(text=f"Next image file name: {content.file_name}", type="text"),
            ImageBlockParam(
                type="image",
                source=Base64ImageSourceParam(
                    type="base64", 
                    data=content.to_base64(), 
                    media_type=content.media_type()
                ),
            )
        ]


class AnthropicToolCallMessageFormatter(MessageContentFormatter):
    def format(self, content: ToolCallAIMessageContent) -> List[ToolUseBlockParam]:
        return [
            ToolUseBlockParam(
                type="tool_use",
                name=content.name,
                input=content.arguments,
                id=content.id,
            )
        ]


class AnthropicToolResponseMessageFormatter(MessageContentFormatter):
    def format(self, content: ToolResponseAIMessageContent) -> List[Any]:
        return [
            ToolResultBlockParam(
                type="tool_result",
                content=content.result,
                tool_use_id=content.id,
            )
        ]


# Gemini formatters
class GeminiTextMessageFormatter(MessageContentFormatter):
    def format(self, content: TextAIMessageContent) -> List[Dict[str, Any]]:
        return [{"text": content.text}]


class GeminiImageMessageFormatter(MessageContentFormatter):
    def format(self, content: ImageAIMessageContent) -> List[Dict[str, Any]]:
        return [
            {"text": f"Next image file name: {content.file_name}"},
            {"inline_data": {"data": content.binary_content, "mime_type": content.media_type()}}
        ]


class GeminiToolCallMessageFormatter(MessageContentFormatter):
    def format(self, content: ToolCallAIMessageContent) -> List[genai_types.Part]:
        return [
            genai_types.Part.from_function_call(name=content.name, args=content.arguments)
        ]


class GeminiToolResponseMessageFormatter(MessageContentFormatter):
    def format(self, content: ToolResponseAIMessageContent) -> List[genai_types.Part]:
        return [
            genai_types.Part.from_function_response(name=content.name, response={"result": content.result})
        ]


# OpenAI Responses formatters
class OpenAIResponsesTextMessageFormatter(MessageContentFormatter):
    def format(self, content: TextAIMessageContent) -> List[ResponseInputContentParam]:
        return [ResponseInputTextParam(type="input_text", text=content.text)]


class OpenAIResponsesImageMessageFormatter(MessageContentFormatter):
    def format(self, content: ImageAIMessageContent) -> List[ResponseInputContentParam]:
        return [
            ResponseInputTextParam(type="input_text", text=f"Next image filename: {content.file_name}"),
            ResponseInputImageParam(type="input_image", image_url=content.to_base64_url(), detail="auto")
        ]


class OpenAIResponsesToolCallMessageFormatter(MessageContentFormatter):
    def format(self, content: ToolCallAIMessageContent) -> List[ResponseFunctionToolCallParam]:
        return [
            ResponseFunctionToolCallParam(
                type="function_call",
                call_id=content.id,
                name=content.name,
                arguments=f"{content.arguments}",
            )
        ]


class OpenAIResponsesToolResponseMessageFormatter(MessageContentFormatter):
    def format(self, content: ToolResponseAIMessageContent) -> List[FunctionCallOutput]:
        return [
            FunctionCallOutput(
                type="function_call_output",
                call_id=content.id,
                output=content.result,
            )
        ]


# OpenAI format formatters
class OpenAITextMessageFormatter(MessageContentFormatter):
    def format(self, content: TextAIMessageContent) -> List[Dict[str, Any]]:
        return [{"type": "text", "text": content.text}]


class OpenAIImageMessageFormatter(MessageContentFormatter):
    def format(self, content: ImageAIMessageContent) -> List[Dict[str, Any]]:
        return [
            {"type": "text", "text": f"Next image filename: {content.file_name}"},
            {"type": "image_url", "image_url": {"url": content.to_base64_url()}}
        ]


class OpenAIToolCallMessageFormatter(MessageContentFormatter):
    def format(self, content: ToolCallAIMessageContent) -> List[Dict[str, Any]]:
        # ToDo: Implement OpenAI tool call formatting
        return []


class OpenAIToolResponseMessageFormatter(MessageContentFormatter):
    def format(self, content: ToolResponseAIMessageContent) -> List[Dict[str, Any]]:
        # ToDo: Implement OpenAI tool response formatting
        return []


# Abstract Factory Pattern
class MessageFormatterFactory(ABC):
    @abstractmethod
    def create_text_formatter(self) -> MessageContentFormatter:
        pass
    
    @abstractmethod
    def create_image_formatter(self) -> MessageContentFormatter:
        pass
    
    @abstractmethod
    def create_tool_call_formatter(self) -> MessageContentFormatter:
        pass

    @abstractmethod
    def create_tool_response_formatter(self) -> MessageContentFormatter:
        pass

    # ToDo: check here Mikhail, looks like we lose all the type hints for content -> List[Any] <-
    def format_content(self, content: AIMessageContent) -> List[Any]:
        if isinstance(content, TextAIMessageContent):
            formatter = self.create_text_formatter()
        elif isinstance(content, ImageAIMessageContent):
            formatter = self.create_image_formatter()
        elif isinstance(content, ToolCallAIMessageContent):
            formatter = self.create_tool_call_formatter()
        elif isinstance(content, ToolResponseAIMessageContent):
            formatter = self.create_tool_response_formatter()
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")
        
        return formatter.format(content)


class AnthropicFormatterFactory(MessageFormatterFactory):
    def create_text_formatter(self) -> MessageContentFormatter:
        return AnthropicTextMessageFormatter()
    
    def create_image_formatter(self) -> MessageContentFormatter:
        return AnthropicImageMessageFormatter()
    
    def create_tool_call_formatter(self) -> MessageContentFormatter:
        return AnthropicToolCallMessageFormatter()
    
    def create_tool_response_formatter(self) -> MessageContentFormatter:
        return AnthropicToolResponseMessageFormatter()


class GeminiFormatterFactory(MessageFormatterFactory):
    def create_text_formatter(self) -> MessageContentFormatter:
        return GeminiTextMessageFormatter()
    
    def create_image_formatter(self) -> MessageContentFormatter:
        return GeminiImageMessageFormatter()
    
    def create_tool_call_formatter(self) -> MessageContentFormatter:
        return GeminiToolCallMessageFormatter()
    
    def create_tool_response_formatter(self) -> MessageContentFormatter:
        return GeminiToolResponseMessageFormatter()


class OpenAIResponsesFormatterFactory(MessageFormatterFactory):
    def create_text_formatter(self) -> MessageContentFormatter:
        return OpenAIResponsesTextMessageFormatter()
    
    def create_image_formatter(self) -> MessageContentFormatter:
        return OpenAIResponsesImageMessageFormatter()
    
    def create_tool_call_formatter(self) -> MessageContentFormatter:
        return OpenAIResponsesToolCallMessageFormatter()
    
    def create_tool_response_formatter(self) -> MessageContentFormatter:
        return OpenAIResponsesToolResponseMessageFormatter()


class OpenAIFormatterFactory(MessageFormatterFactory):
    def create_text_formatter(self) -> MessageContentFormatter:
        return OpenAITextMessageFormatter()
    
    def create_image_formatter(self) -> MessageContentFormatter:
        return OpenAIImageMessageFormatter()
    
    def create_tool_call_formatter(self) -> MessageContentFormatter:
        return OpenAIToolCallMessageFormatter()
    
    def create_tool_response_formatter(self) -> MessageContentFormatter:
        return OpenAIToolResponseMessageFormatter()


# Factory method to get the appropriate factory
def get_formatter_factory(format_type: Union[FormatterProvider, str] = FormatterProvider.OPENAI) -> MessageFormatterFactory:
    # Convert string to enum if needed for backward compatibility
    if isinstance(format_type, str):
        try:
            format_type = FormatterProvider(format_type)
        except ValueError:
            raise ValueError(f"Unknown format type: {format_type}")
    
    if format_type == FormatterProvider.ANTHROPIC:
        return AnthropicFormatterFactory()
    elif format_type == FormatterProvider.GEMINI:
        return GeminiFormatterFactory()
    elif format_type == FormatterProvider.OPENAI_RESPONSES:
        return OpenAIResponsesFormatterFactory()
    elif format_type == FormatterProvider.OPENAI:
        return OpenAIFormatterFactory()
    else:
        raise ValueError(f"Unknown format type: {format_type}")