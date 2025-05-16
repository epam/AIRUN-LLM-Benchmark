# Before use - authorize via amazon aws cli https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#cli-configure-sso-configure
# docs on API https://docs.aws.amazon.com/nova/latest/userguide/using-converse-api.html
import boto3
from Utils.llm.config import Model, default_temperature

client = boto3.client("bedrock-runtime")

def request_bedrock_data(system_prompt, messages, model: Model):
    config = model()

    system = [{"text": system_prompt}]
    formatted_messages = [
        {"role": message['role'], "content": [{"text": message['content']}]}
        for message in messages
    ]

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
        }
    }
