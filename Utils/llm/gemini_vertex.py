from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types

from Utils.llm.config import google_ai_api_key, Model, default_temperature


def request_ai_studio_data(
        system_prompt: str,
        messages: List[Dict[str, str]],
        model: Model
) -> Dict[str, Any]:
    """
    Request data from Google Gemini Vertex AI API.
    Args:
        system_prompt: System prompt for the model
        messages: List of message dictionaries with role and content
        model: Model configuration

    Returns:
        Dictionary containing response content, thoughts, and token usage
    """
    config = model()

    try:
        client = genai.Client(api_key=google_ai_api_key)
    except Exception as e:
        raise Exception(f"Failed to initialize Gemini Vertex client: {e}")

    contents = [
        {"role": message['role'], "parts": [{"text": message['content']}]}
        for message in messages
    ]

    response = client.models.generate_content(
        model=config["model_id"],
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=config["max_tokens"],
            temperature=default_temperature,
            thinking_config=types.ThinkingConfig(
                include_thoughts=True
            )
        )
    )

    text_content: Optional[str] = None
    thinking_content: Optional[str] = None

    metadata = response.usage_metadata

    for part in response.candidates[0].content.parts:
        if not part.text:
            continue
        if part.thought:
            thinking_content = part.text
        else:
            text_content = part.text

    return {
        "content": text_content,
        "thoughts": thinking_content,
        "tokens": {
            "input_tokens": metadata.prompt_token_count,
            "output_tokens": metadata.total_token_count - metadata.prompt_token_count,
            "reasoning_tokens": metadata.thoughts_token_count or 0,
        }
    }


if __name__ == "__main__":
    # Example usage

    data = request_ai_studio_data(
        "You should answer in french.",
        [{"role": "user", "content": "Send me a recipe for banana bread."}],
        Model.Gemini_25_Flash_0520
    )

    print("Thoughts:\n", data["thoughts"])
    print("Content:\n", data["content"])
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
    print(f"Reasoning: {data['tokens']['reasoning_tokens']}")
