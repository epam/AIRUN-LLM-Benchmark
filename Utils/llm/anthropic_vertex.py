from typing import List, Dict, Any, Optional
from anthropic import AnthropicVertex

from Utils.llm.config import Model


def request_anthropic_vertex_data(system_prompt: str, messages: List[Dict[str, str]], model: Model) -> Dict[str, Any]:
    """
    Request data from Anthropic Vertex AI API.

    Args:
        system_prompt: System prompt for the model
        messages: List of message dictionaries with role and content
        model: Model configuration

    Returns:
        Dictionary containing response content, thoughts, and token usage

    Raises:
        Exception: If API request fails or configuration is invalid
    """
    try:
        config = model()
        client = AnthropicVertex(region=config["region"], project_id=config["project_id"])
    except Exception as e:
        raise Exception(f"Failed to initialize Anthropic Vertex client: {e}")

    text_content: Optional[str] = None
    thinking_content: Optional[str] = None

    with client.messages.stream(
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        system=system_prompt,
        messages=messages,
        thinking=config["thinking"],
        model=config["model_id"],
    ) as stream:
        message = stream.get_final_message()

        # Extract content from message
        for item in message.content:
            if item.type == "text":
                text_content = item.text
            elif item.type == "thinking":
                thinking_content = item.thinking

    return {
        "content": text_content,
        "thoughts": thinking_content,
        "tokens": {
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        },
    }


if __name__ == "__main__":
    # Test the API function
    data = request_anthropic_vertex_data(
        "You should answer in french.",
        [{"role": "user", "content": "Send me a recipe for banana bread."}],
        Model.Sonnet_4_Thinking,
    )
    print("Thoughts:\n", data["thoughts"])
    print("Content:\n", data["content"])
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
