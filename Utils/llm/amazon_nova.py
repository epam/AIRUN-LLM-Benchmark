# Before use - authorize via amazon aws cli https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#cli-configure-sso-configure
# docs on API https://docs.aws.amazon.com/nova/latest/userguide/using-converse-api.html
import boto3
from typing import List, Optional
from Utils.llm.config import Model, default_temperature
from Utils.llm.ai_message import AIMessage, AIMessageContentFactory
from Utils.llm.ai_tool import AIToolSet
from Utils.llm.message_converter import get_converter, ConverterProvider
from Utils.llm.response_model import LLMResponse


def request_data(
    system_prompt: str, messages: List[AIMessage], model: Model, tools: Optional[AIToolSet] = None
) -> LLMResponse:
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    config = model()

    converter = get_converter(ConverterProvider.AMAZON_NOVA)
    formatted_messages = converter.convert(messages)

    system = [{"text": system_prompt}]
    inf_params = {"temperature": default_temperature}

    request_params = {
        "modelId": config["model_id"],
        "messages": formatted_messages,
        "system": system,
        "inferenceConfig": inf_params,
    }

    if tools:
        tool_config = {"tools": tools.to_amazon_nova_format()}
        request_params["toolConfig"] = tool_config

    response = client.converse(**request_params)

    message_content = response["output"]["message"]["content"]
    text_content = None
    tool_calls = []

    for content_block in message_content:
        if "text" in content_block:
            text_content = content_block["text"]
        elif "toolUse" in content_block:
            tool_use = content_block["toolUse"]
            tool_calls.append(
                AIMessageContentFactory.create_tool_call(tool_use["name"], tool_use["input"], tool_use["toolUseId"])
            )

    assistant_content = []
    assistant_content.extend(tool_calls)
    if text_content:
        assistant_content.append(AIMessageContentFactory.create_text(text_content))

    return LLMResponse(
        content=text_content,
        tool_calls=tool_calls,
        assistant_content=assistant_content,
        input_tokens=response["usage"]["inputTokens"],
        output_tokens=response["usage"]["outputTokens"],
    )


if __name__ == "__main__":
    resp = request_data(
        system_prompt="You should answer in french.",
        messages=[AIMessage.create_user_message("Send me a recipe for banana bread.")],
        model=Model.AmazonNovaPremier,
        tools=None,
    )

    print("Content:\n", resp.content)
    print("Tokens:")
    print(f"Input: {resp.input_tokens}")
    print(f"Output: {resp.output_tokens}")