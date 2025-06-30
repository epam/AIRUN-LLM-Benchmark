from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import google_ai_api_key, Model, default_temperature
from Utils.llm.ai_message import AIMessage, TextAIMessageContent
from Utils.llm.message_formatter import get_formatter_factory, FormatterProvider


def request_ai_studio_data(system_prompt: str, messages: List[AIMessage], model: Model, tools: Optional[AIToolSet] = None) -> Dict[str, Any]:
    """
    Request data from Google Gemini Vertex AI API.
    Args:
        system_prompt: System prompt for the model
        messages: List of messages with role and content
        model: Model configuration

    Returns:
        Dictionary containing response content, thoughts, and token usage
    """
    config = model()

    try:
        client = genai.Client(api_key=google_ai_api_key)
    except Exception as e:
        raise Exception(f"Failed to initialize Gemini Vertex client: {e}")

    formatter_factory = get_formatter_factory(FormatterProvider.GEMINI)
    
    contents: List[types.ContentDict] = []
    for message in messages:
        parts: list[types.PartDict] = []
        for content in message.content:
            try:
                formatted_content = formatter_factory.format_content(content)
                parts.extend(formatted_content)
            except ValueError as e:
                print(f"Gemini Vertex API: {e}")

        contents.append(
            {
                "role": message.role,
                "parts": parts,
            }
        )

    response = client.models.generate_content(
        model=config["model_id"],
        contents=contents,
        config=types.GenerateContentConfig(
            tools=tools.to_gemini_format() if tools else None,
            system_instruction=system_prompt,
            max_output_tokens=config["max_tokens"],
            temperature=default_temperature,
            thinking_config=types.ThinkingConfig(include_thoughts=True),
        ),
    )

    text_content: Optional[str] = None
    thinking_content: Optional[str] = None
    tool_calls: List[Any] = []

    for part in response.candidates[0].content.parts:
        if part.thought:
            thinking_content = part.text
        elif part.function_call:
            tool_calls.append({
                "name": part.function_call.name,
                "arguments": part.function_call.args,
                "id": part.function_call.id,
            })
        elif part.text:
            text_content = part.text


    metadata = response.usage_metadata
    return {
        "content": text_content,
        "thoughts": thinking_content,
        "tool_calls": tool_calls,
        "tokens": {
            "input_tokens": metadata.prompt_token_count,
            "output_tokens": metadata.total_token_count - metadata.prompt_token_count,
            "reasoning_tokens": metadata.thoughts_token_count or 0,
        },
    }


if __name__ == "__main__":
    # Example usage

    data = request_ai_studio_data(
        "You should answer in french.",
        [AIMessage(role="user",content=[TextAIMessageContent(text="Send me a recipe for banana bread.")])],
        Model.Gemini_25_Flash_0520,
    )

    print("Thoughts:\n", data["thoughts"])
    print("Content:\n", data["content"])
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
    print(f"Reasoning: {data['tokens']['reasoning_tokens']}")
