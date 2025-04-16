import time
import re
import requests
from datetime import datetime
from typing import List, Dict, Literal
from Utils.llm.config import Model, default_temperature, ModelProvider
from Utils.llm.bedrock import request_bedrock_data


class APIException(Exception):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        super().__init__(self.content)


def request_openai_format_data(system_prompt: str, messages: List[dict[str, str]], model: Model):
    config = model()

    skip_system = config.get("skip_system", False)
    extra_params = config.get("extra_params", {})
    system_role_name: Literal["system", "developer"] = config.get("system_role_name", "system")

    headers = {
        'Content-Type': 'application/json',
        'Api-Key': config["api_key"],
        "Authorization": f"Bearer {config['api_key']}",
    }

    payload = {
        'model': config["model_id"],
        'messages': ([] if skip_system else [{'role': system_role_name, 'content': system_prompt}]) + messages,
        'temperature': config.get("temperature", default_temperature),
        **extra_params
    }

    max_tokens = config.get("max_tokens")
    if max_tokens is not None:
        payload['max_tokens'] = max_tokens

    response = requests.post(config["url"], headers=headers, json=payload, timeout=300)

    if not response.ok:
        raise APIException(response.status_code, response.content)

    data = response.json()
    result = {
        "content": data["choices"][0]["message"]["content"],
        "tokens": {
            "input_tokens": data["usage"]["prompt_tokens"],
            "output_tokens": data["usage"]["completion_tokens"],
        }
    }

    if "reasoning_tokens" in data["usage"].get("completion_tokens_details", {}):
        result["tokens"]["reasoning_tokens"] = data["usage"]["completion_tokens_details"]["reasoning_tokens"]

    if data["choices"][0]["message"].get("reasoning_content"):
        result["thoughts"] = data["choices"][0]["message"]["reasoning_content"]

    if model == Model.DeepSeekR1:
        # For DeepSeekR1, we need to extract the reasoning and content separately
        think_match = re.search(r'<think>([\s\S]*?)</think>', result["content"], re.DOTALL)
        result["thoughts"] = think_match.group(1).strip() if think_match else None
        result["content"] = re.sub(r'<think>[\s\S]*?</think>', '', result["content"]).strip()

    return result


def request_openai_response_format_data(system_prompt: str, messages: List[dict[str, str]], model: Model):
    config = model()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config["api_key"]}",
    }

    developer_message = [{
        "role": "developer",
        "content": [{
            "type": "input_text", "text": system_prompt
        }]
    }]

    input_messages = [{
        "role": "user",
        "content": [{"type": "input_text", "text": message["content"]}]
    } for message in messages]

    payload = {
        "model": config["model_id"],
        "input": developer_message + input_messages,
        "temperature": config.get("temperature", default_temperature),
        "text": {
            "format": {
                "type": "text"
            }
        },
        "store": False
    }

    if "max_tokens" in config:
        payload["max_tokens"] = config["max_tokens"]

    if "reasoning_effort" in config:
        payload["reasoning"] = {
            "effort": config["reasoning_effort"]
        }

    response = requests.post(config["url"], headers=headers, json=payload, timeout=300)

    if not response.ok:
        raise APIException(response.status_code, response.content)

    data = response.json()

    content = next(item["content"][0]["text"] for item in data["output"] if item["type"] == "message")
    reasoning = next((item["summary"][0].get("text", None)
                      for item in data["output"]
                      if item["type"] == "reasoning" and len(item["summary"]) > 0),
                     None)

    result = {
        "content": content,
        "thoughts": reasoning,
        "tokens": {
            "input_tokens": data["usage"]["input_tokens"],
            "output_tokens": data["usage"]["output_tokens"],
        }
    }

    if "reasoning_tokens" in data["usage"].get("output_tokens_details", {}):
        result["tokens"]["reasoning_tokens"] = data["usage"]["output_tokens_details"]["reasoning_tokens"]

    return result


def request_google_ai_studio_data(system_prompt: str, messages: List[dict[str, str]], model: Model):
    config = model()

    headers = {
        'Content-Type': 'application/json',
    }

    contents = [
        {"role": message['role'], "parts": [{"text": message['content']}]}
        for message in messages
    ]

    system_instruction = {"role": "user", "parts": [{"text": system_prompt}]} if not config.get("skip_system", False) else None

    payload = {
        "contents": contents,
        "system_instruction": system_instruction,
        "generation_config": {
            "maxOutputTokens": config.get("max_tokens", 8192),
            "temperature": default_temperature,
            "responseMimeType": "text/plain"
        },
    }

    response = requests.post(config["url"], headers=headers, json=payload, timeout=300)

    if not response.ok:
        raise APIException(response.status_code, response.content)

    data = response.json()

    if model in [Model.Gemini_20_Flash_Think_0121, Model.Gemini_25_Pro_0325]:
        parts = data["candidates"][0]["content"]["parts"]
        thoughts = parts[0]["text"] if len(parts) > 1 else None
        content = parts[1]["text"] if thoughts else parts[0]["text"]

        return {
            'thoughts': thoughts,
            'content': content,
            'tokens': {
                "input_tokens": data["usageMetadata"]["promptTokenCount"],
                "output_tokens": data["usageMetadata"]["candidatesTokenCount"],
            }
        }

    return {
        'content': data["candidates"][0]["content"]["parts"][0]["text"],
        'tokens': {
            "input_tokens": data["usageMetadata"]["promptTokenCount"],
            "output_tokens": data["usageMetadata"]["candidatesTokenCount"],
        }
    }


def request_claude_data(system_prompt: str, messages: List[dict[str, str]], model: Model):
    config = model()

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        "Authorization": f"Bearer {config['api_key']}",
    }
    payload = {
        "anthropic_version": config['version'],
        "max_tokens": 4096,
        "stream": False,
        "temperature": default_temperature,
        "system": system_prompt,
        "messages": messages,  # [{"role": "user", "content": prompt}]
        **config.get("extra_params", {})
    }
    response = requests.post(config["url"], headers=headers, json=payload, timeout=300)

    if not response.ok:
        raise APIException(response.status_code, response.content)

    data = response.json()

    text_content = None
    thinking_content = None

    for item in data["content"]:
        if item["type"] == "text":
            text_content = item["text"]
        elif item["type"] == "thinking":
            thinking_content = item["thinking"]

    return {
        "content": text_content,
        "thoughts": thinking_content,
        "tokens": {
            "input_tokens": data["usage"]["input_tokens"],
            "output_tokens": data["usage"]["output_tokens"],
        }
    }


def ask_model(messages: List[dict[str, str]], system_prompt: str, model: Model, attempt: int = 1) -> Dict[str, str]:
    start_time = time.time()
    print(f'\tAttempt {attempt} at {datetime.now()}')
    try:
        data = None

        match model.provider:
            case ModelProvider.AISTUDIO:
                data = request_google_ai_studio_data(system_prompt, messages, model)
            case ModelProvider.VERTEXAI_ANTHROPIC:
                data = request_claude_data(system_prompt, messages, model)
            case ModelProvider.AMAZON:
                data = request_bedrock_data(system_prompt, messages, model)
            case ModelProvider.OPENAI | ModelProvider.AZURE | ModelProvider.XAI | ModelProvider.FIREWORKS:
                data = request_openai_format_data(system_prompt, messages, model)
            case ModelProvider.OPENAI_RESPONSES:
                data = request_openai_response_format_data(system_prompt, messages, model)
            case _:
                raise Exception(f"Unknown model provider: {model.provider}")

        execute_time = time.time() - start_time
        return {
            "thoughts": data.get("thoughts", None),
            "content": data["content"],
            "tokens": data["tokens"],
            "execute_time": execute_time
        }
    except APIException as e:
        print(f"Error: {e.status_code}")
        print(f"Error: {e.content}")
        if e.status_code == 429:
            print('Will try in 1 minute...')
            time.sleep(60)
            return ask_model(messages, system_prompt, model, attempt + 1)
        else:
            if attempt > 2:
                return {
                    "error": f'### Error: {e.content}\n'
                }
            else:
                print("\tTrying again...")
                time.sleep(10)
                return ask_model(messages, system_prompt, model, attempt + 1)
    except requests.exceptions.Timeout:
        if attempt > 2:
            return {
                "error": f'### Error: Timeout error\n'
            }
        print("\tRequest timed out. Trying again...")
        return ask_model(messages, system_prompt, model, attempt + 1)
    except Exception as e:
        print(f"\tError: {str(e)}")
        if attempt > 2:
            return {
                "error": f'### Error: can not get the content\n'
            }
        else:
            print("\tTrying again...")
            time.sleep(5)
            return ask_model(messages, system_prompt, model, attempt + 1)
