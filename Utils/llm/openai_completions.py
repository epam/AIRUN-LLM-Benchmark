from typing import List, Dict, Any, Optional
import re
import json
from openai import OpenAI

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import Model, default_temperature
from Utils.llm.ai_message import AIMessage
from Utils.llm.message_converter import get_converter, ConverterProvider


def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: Optional[AIToolSet] = None
) -> Dict[str, Any]:
    """
    Request data from OpenAI API using the official SDK.

    Args:
        system_prompt: System prompt for the model
        messages: List of messages with role and content
        model: Model configuration
        tools: Set of AI tools to be used in the request

    Returns:
        Dictionary containing response content, thoughts, tool calls, and token usage

    Raises:
        Exception: If API request fails or configuration is invalid
    """
    try:
        config = model()

        # Initialize OpenAI client with appropriate base URL and API key
        client_kwargs = {"api_key": config["api_key"]}
        if "url" in config and config["url"] != "https://api.openai.com/v1":
            client_kwargs["base_url"] = config["url"]

        client = OpenAI(**client_kwargs)
    except Exception as e:
        raise Exception(f"Failed to initialize OpenAI client: {e}")

    skip_system = config.get("skip_system", False)
    extra_params = config.get("extra_params", {})
    system_role_name = config.get("system_role_name", "system")

    # Prepare messages
    api_messages = []

    if not skip_system:
        api_messages.append({"role": system_role_name, "content": system_prompt})

    converter = get_converter(ConverterProvider.OPENAI_COMPLETIONS)
    formatted_messages = converter.convert(messages)
    api_messages.extend(formatted_messages)

    # Prepare request parameters
    request_params = {
        "model": config["model_id"],
        "messages": api_messages,
        "temperature": config.get("temperature", default_temperature),
        **extra_params,
    }

    max_tokens = config.get("max_tokens")
    if max_tokens is not None:
        request_params["max_tokens"] = max_tokens

    if "reasoning_effort" in config:
        request_params["reasoning_effort"] = config["reasoning_effort"]

    # Add tools if provided
    if tools and len(tools) > 0:
        request_params["tools"] = tools.to_openai_completions_format()
        request_params["tool_choice"] = "auto"

    try:
        response = client.chat.completions.create(**request_params)
    except Exception as e:
        raise Exception(f"OpenAI Completions request failed: {e}")

    # Extract response data
    message = response.choices[0].message
    content = message.content
    thoughts = None
    tool_calls = []

    # Handle reasoning content if available
    if hasattr(message, "reasoning_content") and message.reasoning_content:
        thoughts = message.reasoning_content
    elif hasattr(message, "reasoning") and message.reasoning:
        thoughts = message.reasoning

    # Handle tool calls if present
    if message.tool_calls:
        for tool_call in message.tool_calls:
            try:
                # Parse arguments if they're a string
                arguments = tool_call.function.arguments
                if isinstance(arguments, str):
                    arguments = json.loads(arguments) if arguments else {}

                tool_calls.append(
                    {
                        "name": tool_call.function.name,
                        "arguments": arguments,
                        "id": tool_call.id,
                    }
                )
            except json.JSONDecodeError as e:
                print(f"Error parsing tool call arguments: {e}")
                tool_calls.append(
                    {
                        "name": tool_call.function.name,
                        "arguments": {},
                        "id": tool_call.id,
                    }
                )

    # Handle DeepSeekR1 specific reasoning format
    if model in [Model.DeepSeekR1, Model.DeepSeekR1_0528] and content:
        think_match = re.search(r"<think>([\s\S]*?)</think>", content, re.DOTALL)
        thoughts = think_match.group(1).strip() if think_match else None
        content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()

    # Prepare token usage data
    tokens = {
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
    }

    # Add reasoning tokens if available
    if hasattr(response.usage.completion_tokens_details, "reasoning_tokens"):
        tokens["reasoning_tokens"] = response.usage.completion_tokens_details.reasoning_tokens

    return {
        "content": content,
        "thoughts": thoughts,
        "tool_calls": tool_calls,
        "tokens": tokens,
    }


if __name__ == "__main__":
    # Test the API function
    data = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.GPT41_0414,
        tools=None,
    )
    print("Thoughts:\n", data["thoughts"])
    print("Content:\n", data["content"])
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
