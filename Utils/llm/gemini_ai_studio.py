from typing import List, Optional

from google import genai
from google.genai import types

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import google_ai_api_key, Model
from Utils.llm.ai_message import AIMessage, AIMessageContentFactory
from Utils.llm.message_converter import get_converter, ConverterProvider
from Utils.llm.response_model import LLMResponse

recommended_temperature = 1

def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: Optional[AIToolSet] = None
) -> LLMResponse:
    config = model()

    try:
        client = genai.Client(api_key=google_ai_api_key)
    except Exception as e:
        raise Exception(f"Failed to initialize Gemini Vertex client: {e}")

    converter = get_converter(ConverterProvider.GEMINI)
    contents = converter.convert(messages)

    response = client.models.generate_content(
        model=config["model_id"],
        contents=contents,
        config=types.GenerateContentConfig(
            tools=tools.to_gemini_format() if tools else None,
            system_instruction=system_prompt,
            max_output_tokens=config["max_tokens"],
            temperature=recommended_temperature,
            thinking_config=types.ThinkingConfig(include_thoughts=True, thinking_level=config["thinking_level"])
        ),
    )

    text_content: Optional[str] = None
    thinking_content: Optional[str] = None
    tool_calls = []
    assistant_content = []

    for part in response.candidates[0].content.parts:
        if part.thought:
            thinking_content = part.text
            # Preserve thinking part for multi-turn (Gemini requires all parts returned)
            assistant_content.append(
                AIMessageContentFactory.create_thinking(
                    thinking=part.text,
                    signature=getattr(part, 'thought_signature', None)
                )
            )
        elif part.function_call:
            tc = AIMessageContentFactory.create_tool_call(
                part.function_call.name, part.function_call.args, part.function_call.id,
                getattr(part, 'thought_signature', None)
            )
            tool_calls.append(tc)
            assistant_content.append(tc)
        elif part.text:
            text_content = part.text
            assistant_content.append(AIMessageContentFactory.create_text(part.text))

    metadata = response.usage_metadata
    return LLMResponse(
        content=text_content,
        thoughts=thinking_content,
        tool_calls=tool_calls,
        assistant_content=assistant_content,
        input_tokens=metadata.prompt_token_count,
        output_tokens=metadata.total_token_count - metadata.prompt_token_count,
        reasoning_tokens=metadata.thoughts_token_count or 0,
    )


if __name__ == "__main__":
    resp = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.Gemini_3_Pro_Preview,
        tools=None,
    )

    print("Thoughts:\n", resp.thoughts)
    print("Content:\n", resp.content)
    print("Tokens:")
    print(f"Input: {resp.input_tokens}")
    print(f"Output: {resp.output_tokens}")
    print(f"Reasoning: {resp.reasoning_tokens}")