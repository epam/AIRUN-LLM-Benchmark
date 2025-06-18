# Before use - authorize via amazon aws cli https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#cli-configure-sso-configure
# docs on API https://docs.aws.amazon.com/nova/latest/userguide/using-converse-api.html
import boto3
from Utils.llm.config import Model, default_temperature
from Utils.llm.ai_message import AIMessage, TextAIMessageContent, ImageAIMessageContent


def request_bedrock_data(system_prompt: str, messages: list[AIMessage], model: Model):
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    config = model()

    system = [{"text": system_prompt}]
    formatted_messages = []
    for message in messages:
        content_list = []
        for content in message.content_list:
            if isinstance(content, TextAIMessageContent):
                content_list.append({"text": content.text})
            elif isinstance(content, ImageAIMessageContent):
                content_list.append({"text": f"Next image file name: {content.file_name}"})
                content_list.append(
                    {
                        "image": {
                            "format": content.media_type().split("/")[1],
                            "source": {
                                "bytes": content.binary_content,
                            },
                        },
                    }
                )
            else:
                print(f"Bedrock API: Unsupported content type: {type(content)}")

        formatted_messages.append({"role": message.role, "content": content_list})

    inf_params = {"temperature": default_temperature}

    response = client.converse(
        modelId=config["model_id"],
        messages=formatted_messages,
        system=system,
        inferenceConfig=inf_params,
    )

    return {
        "content": response["output"]["message"]["content"][0]["text"],
        "tokens": {
            "input_tokens": response["usage"]["inputTokens"],
            "output_tokens": response["usage"]["outputTokens"],
        },
    }
