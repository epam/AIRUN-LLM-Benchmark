from typing import List, Optional
import re
import json
from openai import OpenAI

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import Model, default_temperature
from Utils.llm.ai_message import AIMessage, AIMessageContentFactory
from Utils.llm.message_converter import get_converter, ConverterProvider
from Utils.llm.response_model import LLMResponse


def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: Optional[AIToolSet] = None
) -> LLMResponse:
    try:
        config = model()

        client_kwargs = {"api_key": config["api_key"]}
        if "url" in config and config["url"] != "https://api.openai.com/v1":
            client_kwargs["base_url"] = config["url"]

        client = OpenAI(**client_kwargs)
    except Exception as e:
        raise Exception(f"Failed to initialize OpenAI client: {e}")

    skip_system = config.get("skip_system", False)
    extra_params = config.get("extra_params", {})
    system_role_name = config.get("system_role_name", "system")

    api_messages = []

    if not skip_system:
        api_messages.append({"role": system_role_name, "content": system_prompt})

    converter = get_converter(ConverterProvider.OPENAI_COMPLETIONS)
    formatted_messages = converter.convert(messages)
    api_messages.extend(formatted_messages)

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

    if tools and len(tools) > 0:
        request_params["tools"] = tools.to_openai_completions_format()
        request_params["tool_choice"] = "auto"

    try:
        response = client.chat.completions.create(**request_params)
    except Exception as e:
        raise Exception(f"OpenAI Completions request failed: {e}")

    message = response.choices[0].message
    content = message.content
    thoughts = None
    tool_calls = []

    if hasattr(message, "reasoning_content") and message.reasoning_content:
        thoughts = message.reasoning_content
    elif hasattr(message, "reasoning") and message.reasoning:
        thoughts = message.reasoning

    if message.tool_calls:
        for tool_call in message.tool_calls:
            try:
                arguments = tool_call.function.arguments
                if isinstance(arguments, str):
                    arguments = json.loads(arguments) if arguments else {}

                tool_calls.append(
                    AIMessageContentFactory.create_tool_call(tool_call.function.name, arguments, tool_call.id)
                )
            except json.JSONDecodeError as e:
                print(f"Error parsing tool call arguments: {e}")
                tool_calls.append(
                    AIMessageContentFactory.create_tool_call(tool_call.function.name, {}, tool_call.id)
                )

    # Handle DeepSeekR1 specific reasoning format
    if model in [] and content:
        think_match = re.search(r"<think>([\s\S]*?)</think>", content, re.DOTALL)
        thoughts = think_match.group(1).strip() if think_match else None
        content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()

    reasoning_tokens = 0
    if hasattr(response.usage, "completion_tokens_details") and hasattr(response.usage.completion_tokens_details, "reasoning_tokens"):
        reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens or 0

    assistant_content = []
    assistant_content.extend(tool_calls)
    if content:
        assistant_content.append(AIMessageContentFactory.create_text(content))

    return LLMResponse(
        content=content,
        thoughts=thoughts,
        tool_calls=tool_calls,
        assistant_content=assistant_content,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        reasoning_tokens=reasoning_tokens,
    )


if __name__ == "__main__":
    resp = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.Kimi_K2p5,
        tools=None,
    )
    print("Thoughts:\n", resp.thoughts)
    print("Content:\n", resp.content)
    print("Tokens:")
    print(f"Input: {resp.input_tokens}")
    print(f"Output: {resp.output_tokens}")
    if resp.reasoning_tokens:
        print(f"Reasoning: {resp.reasoning_tokens}")