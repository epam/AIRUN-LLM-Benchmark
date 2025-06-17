from typing import List, Dict, Any, Optional
from anthropic import AnthropicVertex
from anthropic.types import TextBlockParam, ImageBlockParam, Base64ImageSourceParam

from Utils.llm.config import Model
from Utils.llm.ai_message import AIMessage, TextAIMessageContent, ImageAIMessageContent


def request_anthropic_vertex_data(system_prompt: str, messages: List[AIMessage], model: Model) -> Dict[str, Any]:
    """
    Request data from Anthropic Vertex AI API.

    Args:
        system_prompt: System prompt for the model
        messages: List of messages with role and content
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

    api_messages = []
    for message in messages:
        api_content = []
        for content in message.content_list:
            if isinstance(content, TextAIMessageContent):
                api_content.append(TextBlockParam(text=content.text, type="text"))
            elif isinstance(content, ImageAIMessageContent):
                api_content.append(TextBlockParam(text=f"Next image file name: {content.file_name}", type="text"))
                api_content.append(
                    ImageBlockParam(
                        type="image",
                        source=Base64ImageSourceParam(
                            type="base64", data=content.to_base64(), media_type=content.media_type()
                        ),
                    )
                )
            else:
                print(f"Anthropic Vertex API: Unsupported content type: {type(content)}")

        api_messages.append({"role": message.role, "content": api_content})

    with client.messages.stream(
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        system=system_prompt,
        messages=api_messages,
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
    message = AIMessage(
        role="user",
        content_list=[TextAIMessageContent(text="Send me a recipe for banana bread.")],
    )
    data = request_anthropic_vertex_data(
        system_prompt="You should answer in french.",
        messages=[message],
        model=Model.Sonnet_4_Thinking,
    )
    print("Thoughts:\n", data["thoughts"])
    print("Content:\n", data["content"])
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
