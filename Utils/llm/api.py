import time
import requests
from datetime import datetime
from typing import Any, List, Dict

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import Model, ModelProvider
from Utils.llm.anthropic_vertex import request_data as request_anthropic_vertex_data
from Utils.llm.amazon_nova import request_data as request_amazon_nova_data
from Utils.llm.gemini_ai_studio import request_data as request_gemini_aistudio_data
from Utils.llm.responses_api import request_data as request_openai_responses_data
from Utils.llm.openai_completions import request_data as request_openai_completions_data
from Utils.llm.ai_message import AIMessage


class APIException(Exception):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        super().__init__(self.content)


def ask_model(
    messages: List[AIMessage], system_prompt: str, model: Model, attempt: int = 1, tools: AIToolSet = None
) -> Dict[str, Any]:
    start_time = time.time()
    print(f"\tAttempt {attempt} at {datetime.now()}")
    try:
        data = None

        match model.provider:
            case ModelProvider.AISTUDIO:
                data = request_gemini_aistudio_data(system_prompt, messages, model, tools)
            case ModelProvider.VERTEXAI_ANTHROPIC:
                data = request_anthropic_vertex_data(system_prompt, messages, model, tools)
            case ModelProvider.AMAZON:
                data = request_amazon_nova_data(system_prompt, messages, model, tools)
            case ModelProvider.OPENAI | ModelProvider.AZURE | ModelProvider.XAI | ModelProvider.FIREWORKS:
                data = request_openai_completions_data(system_prompt, messages, model, tools)
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
