from typing import List, Dict, Any, Optional
from anthropic import AnthropicVertex

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import Model
from Utils.llm.ai_message import AIMessage
from Utils.llm.message_converter import get_converter, ConverterProvider


def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: Optional[AIToolSet] = None
) -> Dict[str, Any]:
    """
    Request data from Anthropic Vertex AI API.

    Args:
        system_prompt: System prompt for the model
        messages: List of messages with role and content
        model: Model configuration
        tools: Set of AI tools to be used in the request

    Returns:
        Dictionary containing response content, thoughts, and token usage

    Raises:
        Exception: If API request fails or configuration is invalid
    """
    try:
        config = model()
        client = AnthropicVertex(region=config["region"], project_id=config["project_id"])
    except Exception as e:
        raise Exception(f"Failed to initialize Anthropic Vertex client: {e}")

    text_content: Optional[str] = None
    thinking_content: Optional[str] = None
    tool_calls: List[Any] = []

    converter = get_converter(ConverterProvider.ANTHROPIC)
    api_messages = converter.convert(messages)

    with client.messages.stream(
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        system=system_prompt,
        messages=api_messages,
        thinking=config["thinking"],
        model=config["model_id"],
        tools=tools.to_anthropic_format() if tools else [],
    ) as stream:
        message = stream.get_final_message()

        # Extract content from message
        for item in message.content:
            if item.type == "text":
                text_content = item.text
            elif item.type == "thinking":
                thinking_content = item.thinking
            elif item.type == "tool_use":
                tool_calls.append(
                    {
                        "name": item.name,
                        "arguments": item.input,
                        "id": item.id,
                    }
                )

    return {
        "content": text_content,
        "thoughts": thinking_content,
        "tool_calls": tool_calls,
        "tokens": {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        },
    }


if __name__ == "__main__":
    # Test the API function
    data = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.Sonnet_4,
        tools=None,
    )

    print("Thoughts:\n", data["thoughts"])
    print("Content:\n", data["content"])
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
