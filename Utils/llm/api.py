import time
import requests
from datetime import datetime
from Utils.llm.config import API, Model, temperature
from Utils.llm.bedrock import request_bedrock_data


class APIException(Exception):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        super().__init__(self.content)


def request_openai_format_data(system_prompt, messages, model):
    config = API[model]()

    skip_system = config.get("skip_system", False)

    headers = {
        'Content-Type': 'application/json',
        'Api-Key': config["api_key"],
        "Authorization": f"Bearer {config['api_key']}",
    }

    payload = {
        'model': config["model_id"],
        'messages': ([] if skip_system else [{'role': 'system', 'content': f'{system_prompt}'}]) + messages,
        'temperature': temperature,
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

    return result


def request_gemini_pro_data(system_prompt, messages):
    config = API[Model.GeminiPro]()

    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {config['api_key']}",
    }
    contents = [
        {"role": message['role'], "parts": [{"text": message['content']}]}
        for message in messages
    ]
    payload = {
        "contents": contents,
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "generation_config": {
            "maxOutputTokens": 8192,
            "temperature": temperature,
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            }
        ],
    }
    response = requests.post(config["url"], headers=headers, json=payload, timeout=300)

    if not response.ok:
        raise APIException(response.status_code, response.content)

    data = response.json()
    return {
        'content': data["candidates"][0]["content"]["parts"][0]["text"],
        'tokens': {
            "input_tokens": data["usageMetadata"]["promptTokenCount"],
            "output_tokens": data["usageMetadata"]["candidatesTokenCount"],
        }
    }


def request_google_ai_studio_data(system_prompt, messages, model):
    config = API[model]()

    headers = {
        'Content-Type': 'application/json',
    }

    contents = [
        {"role": message['role'], "parts": [{"text": message['content']}]}
        for message in messages
    ]

    payload = {
        "contents": contents,
        "system_instruction": {"role": "user", "parts": [{"text": system_prompt}]},
        "generation_config": {
            "maxOutputTokens": 8192,
            "temperature": temperature,
            "responseMimeType": "text/plain"
        },
    }

    response = requests.post(config["url"], headers=headers, json=payload, timeout=300)

    if not response.ok:
        raise APIException(response.status_code, response.content)

    data = response.json()
    return {
        'content': data["candidates"][0]["content"]["parts"][0]["text"],
        'tokens': {
            "input_tokens": data["usageMetadata"]["promptTokenCount"],
            "output_tokens": data["usageMetadata"]["candidatesTokenCount"],
        }
    }


def request_claude_data(system_prompt, messages, model):
    config = API[model]()  # Claude Opus or Sonnet

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        "Authorization": f"Bearer {config['api_key']}",
    }
    payload = {
        "anthropic_version": config['version'],
        "max_tokens": 4096,
        "stream": False,
        "temperature": temperature,
        "system": system_prompt,
        "messages": messages  # [{"role": "user", "content": prompt}]
    }
    response = requests.post(config["url"], headers=headers, json=payload, timeout=300)

    if not response.ok:
        raise APIException(response.status_code, response.content)

    data = response.json()
    return {
        'content': data["content"][0]["text"],
        'tokens': {
            "input_tokens": data["usage"]["input_tokens"],
            "output_tokens": data["usage"]["output_tokens"],
        }
    }


def ask_model(messages, system_prompt, model, attempt=1):
    start_time = time.time()
    print(f'\tAttempt {attempt} at {datetime.now()}')
    try:
        data = None

        match model:
            case Model.GeminiPro:
                data = request_gemini_pro_data(system_prompt, messages)
            case Model.GeminiPro_0801 | Model.Gemini_15_Pro_002 | Model.GeminiPro_1114 | Model.GeminiPro_1121:
                data = request_google_ai_studio_data(system_prompt, messages, model)
            case Model.Opus_3 | Model.Sonnet_35 | Model.Sonnet_35v2 | Model.Haiku_35:
                data = request_claude_data(system_prompt, messages, model)
            case Model.AmazonNovaPro:
                data = request_bedrock_data(system_prompt, messages, model)
            case _:
                data = request_openai_format_data(system_prompt, messages, model)

        execute_time = time.time() - start_time
        return {
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
