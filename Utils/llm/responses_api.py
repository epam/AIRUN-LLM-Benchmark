import json
from datetime import datetime
from time import sleep
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.shared_params import Reasoning
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputItemParam,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningItem,
    ResponseFunctionToolCall,
)

from Utils.llm.ai_message import AIMessage, TextAIMessageContent
from Utils.llm.ai_tool import AIToolSet
from Utils.llm.message_converter import get_converter, ConverterProvider
from Utils.llm.config import Model


def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: AIToolSet = None
) -> Dict[str, Any]:
    """
    Request data from OpenAI Responses API.

    Args:
        system_prompt: System prompt for the model
        messages: List of messages with role and content
        model: Model configuration

    Returns:
        Dictionary containing response content, thoughts, and token usage

    Raises:
        Exception: If API request fails or configuration is invalid
    """
    config = model()
    developer_message: List[ResponseInputItemParam] = [EasyInputMessageParam(role="developer", content=system_prompt)]

    converter = get_converter(ConverterProvider.OPENAI_RESPONSES)
    input_messages = converter.convert(messages)

    try:
        client = OpenAI()
        resp = client.responses.create(
            tools=tools.to_openai_responses_format() if tools else None,
            model=config["model_id"],
            input=developer_message + input_messages,
            max_output_tokens=config["max_tokens"],
            temperature=config["temperature"],
            reasoning=Reasoning(effort=config["reasoning_effort"]),
            background=True,
        )
    except Exception as e:
        raise Exception(f"Failed to initialize OpenAI client or create response: {e}")

    print(f"Response ID: {resp.id}")

    try:
        while resp.status in {"queued", "in_progress"}:
            print(f"\r\tResponse status: {resp.status} | Last update: {datetime.now()}", end="", flush=True)
            sleep(10)
            resp = client.responses.retrieve(resp.id)
        print()
    except Exception as e:
        raise Exception(f"Failed to retrieve response: {e}")

    response = resp.output

    content = next(
        (
            item.content[0].text
            for item in response
            if isinstance(item, ResponseOutputMessage)
            and isinstance(item.content[0], ResponseOutputText)
            and len(item.content) > 0
        ),
        None,
    )
    reasoning = (
        "\n".join(
            summary.text
            for item in response
            if isinstance(item, ResponseReasoningItem)
            for summary in item.summary
            if summary.text
        )
        or None
    )

    tool_calls = [
        {
            "name": item.name,
            "arguments": json.loads(item.arguments),
            "id": item.call_id,
        }
        for item in response
        if isinstance(item, ResponseFunctionToolCall)
    ]

    result = {
        "content": content,
        "thoughts": reasoning,
        "tool_calls": tool_calls,
        "tokens": {
            "input_tokens": resp.usage.input_tokens if resp.usage else None,
            "output_tokens": resp.usage.output_tokens if resp.usage else None,
            "reasoning_tokens": (resp.usage.output_tokens_details.reasoning_tokens if resp.usage else None),
        },
    }

    return result


if __name__ == "__main__":
    data = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.OpenAi_o4_mini_0416,
        tools=None,
    )

    print("Thoughts:", data["thoughts"], sep="\n")
    print("Content:", data["content"], sep="\n")
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
    print(f"Reasoning: {data['tokens']['reasoning_tokens']}")
