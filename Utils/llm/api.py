import time
import re
import requests
from datetime import datetime
from typing import Any, List, Dict, Literal

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import Model, default_temperature, ModelProvider
from Utils.llm.anthropic_vertex import request_anthropic_vertex_data
from Utils.llm.bedrock import request_bedrock_data
from Utils.llm.gemini_ai_studio import request_ai_studio_data
from Utils.llm.responses_api import request_openai_responses_data
from Utils.llm.ai_message import AIMessage
from Utils.llm.message_formatter import get_formatter_factory, FormatterProvider


class APIException(Exception):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        super().__init__(self.content)


def format_openai_messages(messages):
    formatter_factory = get_formatter_factory(FormatterProvider.OPENAI)
    api_messages = []
    for message in messages:
        api_content = []
        for content in message.content:
            try:
                formatted_content = formatter_factory.format_content(content)
                api_content.extend(formatted_content)
            except ValueError as e:
                print(f"OpenAI format API: {e}")

        api_message = {
            "role": message.role,
            "content": api_content,
        }
        api_messages.append(api_message)
    return api_messages


def request_openai_format_data(system_prompt: str, messages: List[AIMessage], model: Model):
    config = model()

    skip_system = config.get("skip_system", False)
    extra_params = config.get("extra_params", {})
    system_role_name: Literal["system", "developer"] = config.get("system_role_name", "system")

    headers = {
        "Content-Type": "application/json",
        "Api-Key": config["api_key"],
        "Authorization": f"Bearer {config['api_key']}",
    }

    payload = {
        "model": config["model_id"],
        "messages": [],
        "temperature": config.get("temperature", default_temperature),
        **extra_params,
    }

    if not skip_system:
        payload["messages"].append({"role": system_role_name, "content": system_prompt})

    api_messages = format_openai_messages(messages)
    payload["messages"].extend(api_messages)

    max_tokens = config.get("max_tokens")
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    if "reasoning_effort" in config:
        payload["reasoning_effort"] = config["reasoning_effort"]

    response = requests.post(config["url"], headers=headers, json=payload, timeout=300)

    if not response.ok:
        raise APIException(response.status_code, response.content)

    data = response.json()
    result = {
        "content": data["choices"][0]["message"]["content"],
        "tokens": {
            "input_tokens": data["usage"]["prompt_tokens"],
            "output_tokens": data["usage"]["completion_tokens"],
        },
    }

    if "reasoning_tokens" in data["usage"].get("completion_tokens_details", {}):
        result["tokens"]["reasoning_tokens"] = data["usage"]["completion_tokens_details"]["reasoning_tokens"]

    if data["choices"][0]["message"].get("reasoning_content"):
        result["thoughts"] = data["choices"][0]["message"]["reasoning_content"]

    if model in [Model.DeepSeekR1, Model.DeepSeekR1_0528]:
        # For DeepSeekR1, we need to extract the reasoning and content separately
        think_match = re.search(r"<think>([\s\S]*?)</think>", result["content"], re.DOTALL)
        result["thoughts"] = think_match.group(1).strip() if think_match else None
        result["content"] = re.sub(r"<think>[\s\S]*?</think>", "", result["content"]).strip()

    return result


def ask_model(
    messages: List[AIMessage], system_prompt: str, model: Model, attempt: int = 1, tools: AIToolSet = None
) -> Dict[str, Any]:
    start_time = time.time()
    print(f"\tAttempt {attempt} at {datetime.now()}")
    try:
        data = None

        match model.provider:
            case ModelProvider.AISTUDIO:
                data = request_ai_studio_data(system_prompt, messages, model, tools)
            case ModelProvider.VERTEXAI_ANTHROPIC:
                data = request_anthropic_vertex_data(system_prompt, messages, model, tools)
            case ModelProvider.AMAZON:
                data = request_bedrock_data(system_prompt, messages, model)
            case ModelProvider.OPENAI | ModelProvider.AZURE | ModelProvider.XAI | ModelProvider.FIREWORKS:
                data = request_openai_format_data(system_prompt, messages, model)
            case ModelProvider.OPENAI_RESPONSES:
                data = request_openai_responses_data(system_prompt, messages, model, tools)
            case _:
                raise Exception(f"Unknown model provider: {model.provider}")

        execute_time = time.time() - start_time
        return {
            "thoughts": data.get("thoughts", None),
            "content": data["content"],
            "tokens": data["tokens"],
            "tool_calls": data.get("tool_calls", []),
            "execute_time": execute_time,
        }
    except APIException as e:
        print(f"Error: {e.status_code}")
        print(f"Error: {e.content}")
        if e.status_code == 429:
            print("Will try in 1 minute...")
            time.sleep(60)
            return ask_model(messages, system_prompt, model, attempt + 1, tools)
        else:
            if attempt > 2:
                return {"error": f"### Error: {e.content}\n"}
            else:
                print("\tTrying again...")
                time.sleep(10)
                return ask_model(messages, system_prompt, model, attempt + 1, tools)
    except requests.exceptions.Timeout:
        if attempt > 2:
            return {"error": f"### Error: Timeout error\n"}
        print("\tRequest timed out. Trying again...")
        return ask_model(messages, system_prompt, model, attempt + 1, tools)
    except Exception as e:
        print(f"\tError: {str(e)}")
        if attempt > 2:
            return {"error": f"### Error: can not get the content\n"}
        else:
            print("\tTrying again...")
            time.sleep(5)
            return ask_model(messages, system_prompt, model, attempt + 1, tools)
