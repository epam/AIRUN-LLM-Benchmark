import json
from datetime import datetime
from time import sleep
from typing import List, Optional
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

from Utils.llm.ai_message import AIMessage, AIMessageContentFactory
from Utils.llm.ai_tool import AIToolSet
from Utils.llm.message_converter import get_converter, ConverterProvider
from Utils.llm.config import Model, default_temperature
from Utils.llm.response_model import LLMResponse


def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: AIToolSet = None
) -> LLMResponse:
    config = model()
    developer_message: List[ResponseInputItemParam] = [EasyInputMessageParam(role="developer", content=system_prompt)]

    converter = get_converter(ConverterProvider.OPENAI_RESPONSES)
    input_messages = converter.convert(messages)

    verbosity_level = config.get("verbosity")
    verbosity = {"verbosity": verbosity_level} if verbosity_level else None
    background = config.get("background", False)

    try:
        client = OpenAI()
        resp = client.responses.create(
            text=verbosity,
            tools=tools.to_openai_responses_format() if tools else None,
            model=config["model_id"],
            input=developer_message + input_messages,
            include=["reasoning.encrypted_content"],
            max_output_tokens=config["max_tokens"],
            temperature=config.get("temperature", default_temperature),
            reasoning=Reasoning(effort=config.get("reasoning_effort", None), summary="auto"),
            background=background,
            # store=True
        )
    except Exception as e:
        raise Exception(f"Failed to initialize Responses API client or create response: {e}")

    if background:
        try:
            while resp.status in {"queued", "in_progress"}:
                print(f"\r\tResponse status: {resp.status} | Last update: {datetime.now()}", end="", flush=True)
                sleep(10)
                resp = client.responses.retrieve(resp.id)

            print()
        except Exception as e:
            raise Exception(f"Failed to retrieve response: {e}")

    response = resp.output

    text_content: Optional[str] = None
    reasoning_text: Optional[str] = None

    tool_calls = []
    assistant_content = []

    for item in response:
        if isinstance(item, ResponseReasoningItem):
            reasoning_text = "\n".join(
                summary.text for summary in item.summary if summary.text
            ) or None
            summary_list = [{"type": s.type, "text": s.text} for s in item.summary if s.text]
            assistant_content.append(
                AIMessageContentFactory.create_reasoning(
                    reasoning_id=item.id,
                    summary=summary_list,
                    encrypted_content=item.encrypted_content,
                )
            )
        elif isinstance(item, ResponseOutputMessage):
            if len(item.content) > 0 and isinstance(item.content[0], ResponseOutputText):
                text_content = item.content[0].text
                assistant_content.append(AIMessageContentFactory.create_text(text_content))
        elif isinstance(item, ResponseFunctionToolCall):
            tc = AIMessageContentFactory.create_tool_call(item.name, json.loads(item.arguments), item.call_id, item_id=item.id)
            tool_calls.append(tc)
            assistant_content.append(tc)

    return LLMResponse(
        content=text_content,
        thoughts=reasoning_text,
        tool_calls=tool_calls,
        assistant_content=assistant_content,
        input_tokens=resp.usage.input_tokens if resp.usage else 0,
        output_tokens=resp.usage.output_tokens if resp.usage else 0,
        reasoning_tokens=resp.usage.output_tokens_details.reasoning_tokens if resp.usage else 0,
    )


if __name__ == "__main__":
    resp = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.GPT52_1211_high,
        tools=None,
    )

    print("Thoughts:", resp.thoughts, sep="\n")
    print("Content:", resp.content, sep="\n")
    print("Tokens:")
    print(f"Input: {resp.input_tokens}")
    print(f"Output: {resp.output_tokens}")
    print(f"Reasoning: {resp.reasoning_tokens}")