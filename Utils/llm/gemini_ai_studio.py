from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import google_ai_api_key, Model, default_temperature
from Utils.llm.ai_message import AIMessage
from Utils.llm.message_converter import get_converter, ConverterProvider

recommended_temperature = 1

def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: Optional[AIToolSet] = None
) -> Dict[str, Any]:
    """
    Request data from Google Gemini Vertex AI API.
    Args:
        system_prompt: System prompt for the model
        messages: List of messages with role and content
        model: Model configuration
        tools: Optional set of tools to use with the model

    Returns:
        Dictionary containing response content, thoughts, and token usage
    """
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
    tool_calls: List[Any] = []

    for part in response.candidates[0].content.parts:
        if part.thought:
            thinking_content = part.text
        elif part.function_call:
            tool_call_data = {
                "name": part.function_call.name,
                "arguments": part.function_call.args,
                "id": part.function_call.id,
            }
            # Extract thought_signature if present
            if hasattr(part, 'thought_signature') and part.thought_signature:
                tool_call_data["signature"] = part.thought_signature
            tool_calls.append(tool_call_data)
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

    data = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.Gemini_3_Pro_Preview,
        tools=None,
    )

    print("Thoughts:\n", data["thoughts"])
    print("Content:\n", data["content"])
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
    print(f"Reasoning: {data['tokens']['reasoning_tokens']}")
