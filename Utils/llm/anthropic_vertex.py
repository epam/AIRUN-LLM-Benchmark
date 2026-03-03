from typing import List, Optional
from anthropic import AnthropicVertex

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import Model
from Utils.llm.ai_message import AIMessage, AIMessageContentFactory
from Utils.llm.message_converter import get_converter, ConverterProvider
from Utils.llm.response_model import LLMResponse


def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: Optional[AIToolSet] = None
) -> LLMResponse:
    try:
        config = model()
        client = AnthropicVertex(region=config["region"], project_id=config["project_id"])
    except Exception as e:
        raise Exception(f"Failed to initialize Anthropic Vertex client: {e}")

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

    text_content: Optional[str] = None
    thoughts_parts: List[str] = []
    tool_calls = []
    assistant_content = []

    for item in message.content:
        if item.type == "thinking":
            thoughts_parts.append(item.thinking)
            assistant_content.append(
                AIMessageContentFactory.create_thinking(
                    thinking=item.thinking, signature=getattr(item, "signature", None)
                )
            )
        elif item.type == "redacted_thinking":
            thoughts_parts.append(f"[REDACTED THINKING - {len(item.data)} bytes]")
            assistant_content.append(AIMessageContentFactory.create_redacted_thinking(data=item.data))
        elif item.type == "tool_use":
            tc = AIMessageContentFactory.create_tool_call(item.name, item.input, item.id)
            tool_calls.append(tc)
            assistant_content.append(tc)
        elif item.type == "text":
            text_content = item.text
            assistant_content.append(AIMessageContentFactory.create_text(item.text))

    return LLMResponse(
        content=text_content,
        thoughts="\n\n".join(thoughts_parts) if thoughts_parts else None,
        tool_calls=tool_calls,
        assistant_content=assistant_content,
        input_tokens=message.usage.input_tokens,
        output_tokens=message.usage.output_tokens,
    )


if __name__ == "__main__":
    resp = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.Sonnet_46,
        tools=None,
    )

    print("Thoughts:\n", resp.thoughts)
    print("Content:\n", resp.content)
    print("Tokens:")
    print(f"Input: {resp.input_tokens}")
    print(f"Output: {resp.output_tokens}")