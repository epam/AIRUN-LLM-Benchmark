from time import sleep
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.shared_params import Reasoning
from openai.types.responses import EasyInputMessageParam

from Utils.llm.config import Model


def request_openai_responses_data(system_prompt: str, messages: List[Dict[str, str]], model: Model) -> Dict[str, Any]:
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
    developer_message = [EasyInputMessageParam(role="developer", content=system_prompt)]
    input_messages = [
        EasyInputMessageParam(role="user" if message["role"] == "user" else "assistant", content=message["content"])
        for message in messages
    ]

    try:
        client = OpenAI()
        resp = client.responses.create(
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
            print(f"Response status: {resp.status}")
            sleep(30)
            resp = client.responses.retrieve(resp.id)
    except Exception as e:
        raise Exception(f"Failed to retrieve response: {e}")

    response = resp.output

    content = next(item.content[0].text for item in response if item.type == "message")
    reasoning = next(
        (item.summary[0].get("text", None) for item in response if item.type == "reasoning" and len(item.summary) > 0),
        None,
    )

    result = {
        "content": content,
        "thoughts": reasoning,
        "tokens": {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
            "reasoning_tokens": resp.usage.output_tokens_details.reasoning_tokens,  # Default to 0 if not present
        },
    }

    return result


if __name__ == "__main__":
    data = request_openai_responses_data(
        system_prompt="You should answer in french.",
        messages=[{"role": "user", "content": "Send me a recipe for banana bread."}],
        model=Model.OpenAi_o3_0416,
    )

    print("Thoughts:", data["thoughts"], sep="\n")
    print("Content:", data["content"], sep="\n")
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
    print(f"Reasoning: {data['tokens']['reasoning_tokens']}")
