from datetime import datetime
from time import sleep
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.shared_params import Reasoning
from openai.types.responses import (
    EasyInputMessageParam,
    ResponseInputContentParam,
    ResponseInputTextParam,
    ResponseInputImageParam,
    ResponseInputItemParam,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningItem,
)

from Utils.llm.ai_message import AIMessage, TextAIMessageContent, ImageAIMessageContent
from Utils.llm.config import Model


def request_openai_responses_data(system_prompt: str, messages: List[AIMessage], model: Model) -> Dict[str, Any]:
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
    input_messages: List[ResponseInputItemParam] = []
    for message in messages:
        api_message_content: List[ResponseInputContentParam] = []
        for content in message.content_list:
            if isinstance(content, TextAIMessageContent):
                api_message_content.append(ResponseInputTextParam(type="input_text", text=content.text))
            elif isinstance(content, ImageAIMessageContent):
                api_message_content.append(
                    ResponseInputTextParam(type="input_text", text=f"Next image filename: {content.file_name}")
                )
                api_message_content.append(
                    ResponseInputImageParam(type="input_image", image_url=content.to_base64_url(), detail="auto")
                )
            else:
                print(f"OpenAI responses API: Unsupported content type: {type(content)}")
        input_messages.append(
            EasyInputMessageParam(role="user" if message.role == "user" else "assistant", content=api_message_content)
        )

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
            print(f"\r\tResponse status: {resp.status} | Last update: {datetime.now()}", end="", flush=True)
            sleep(30)
            resp = client.responses.retrieve(resp.id)
        print()
    except Exception as e:
        raise Exception(f"Failed to retrieve response: {e}")

    response = resp.output

    content = next(
        item.content[0].text
        for item in response
        if isinstance(item, ResponseOutputMessage)
        and isinstance(item.content[0], ResponseOutputText)
        and len(item.content) > 0
    )
    reasoning = "\n".join(
        summary.text
        for item in response
        if isinstance(item, ResponseReasoningItem)
        for summary in item.summary
        if summary.text
    )

    result = {
        "content": content,
        "thoughts": reasoning,
        "tokens": {
            "input_tokens": resp.usage.input_tokens if resp.usage else None,
            "output_tokens": resp.usage.output_tokens if resp.usage else None,
            "reasoning_tokens": (resp.usage.output_tokens_details.reasoning_tokens if resp.usage else None),
        },
    }

    return result


if __name__ == "__main__":
    data = request_openai_responses_data(
        system_prompt="You should answer in french.",
        messages=[
            AIMessage(role="user", content_list=[TextAIMessageContent(text="Send me a recipe for banana bread.")])
        ],
        model=Model.OpenAi_o3_0416,
    )

    print("Thoughts:", data["thoughts"], sep="\n")
    print("Content:", data["content"], sep="\n")
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
    print(f"Reasoning: {data['tokens']['reasoning_tokens']}")
