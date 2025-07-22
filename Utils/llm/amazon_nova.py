# Before use - authorize via amazon aws cli https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#cli-configure-sso-configure
# docs on API https://docs.aws.amazon.com/nova/latest/userguide/using-converse-api.html
import boto3
from typing import List, Dict, Any, Optional
from Utils.llm.config import Model, default_temperature
from Utils.llm.ai_message import AIMessage
from Utils.llm.ai_tool import AIToolSet
from Utils.llm.message_converter import get_converter, ConverterProvider


def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: Optional[AIToolSet] = None
) -> Dict[str, Any]:
    """
    Request data from AWS Bedrock API.

    Args:
        system_prompt: System prompt for the model
        messages: List of AIMessage objects
        model: Model configuration
        tools: Optional set of AI tools to be used in the request

    Returns:
        Dictionary containing response content, thoughts, tool calls, and token usage
    """
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    config = model()

    # Use converter for message formatting
    converter = get_converter(ConverterProvider.AMAZON_NOVA)
    formatted_messages = converter.convert(messages)

    system = [{"text": system_prompt}]
    inf_params = {"temperature": default_temperature}

    # Prepare request parameters
    request_params = {
        "modelId": config["model_id"],
        "messages": formatted_messages,
        "system": system,
        "inferenceConfig": inf_params,
    }

    # Add tools if provided
    if tools:
        tool_config = {"tools": tools.to_amazon_nova_format()}
        request_params["toolConfig"] = tool_config

    response = client.converse(**request_params)

    # Extract content and tool calls from response
    message_content = response["output"]["message"]["content"]
    text_content = None
    tool_calls = []

    for content_block in message_content:
        if "text" in content_block:
            text_content = content_block["text"]
        elif "toolUse" in content_block:
            tool_use = content_block["toolUse"]
            tool_calls.append(
                {
                    "name": tool_use["name"],
                    "arguments": tool_use["input"],
                    "id": tool_use["toolUseId"],
                }
            )

    return {
        "content": text_content,
        "thoughts": None,  # Amazon Nova models doesn't have reasoning tokens like some other APIs
        "tool_calls": tool_calls,
        "tokens": {
            "input_tokens": response["usage"]["inputTokens"],
            "output_tokens": response["usage"]["outputTokens"],
        },
    }


if __name__ == "__main__":
    # Example usage
    data = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.AmazonNovaPremier,
        tools=None,
    )

    print("Content:\n", data["content"])
    print("Tokens:")
    print(f"Input: {data['tokens']['input_tokens']}")
    print(f"Output: {data['tokens']['output_tokens']}")
