import time
import requests
from datetime import datetime
from typing import List

from Utils.llm.ai_tool import AIToolSet
from Utils.llm.config import Model, ModelProvider
from Utils.llm.anthropic_vertex import request_data as request_anthropic_vertex_data
from Utils.llm.amazon_nova import request_data as request_amazon_nova_data
from Utils.llm.gemini_ai_studio import request_data as request_gemini_aistudio_data
from Utils.llm.responses_api import request_data as request_openai_responses_data
from Utils.llm.openai_completions import request_data as request_openai_completions_data
from Utils.llm.ai_message import AIMessage
from Utils.llm.response_model import LLMResponse


class APIException(Exception):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content
        super().__init__(self.content)


def ask_model(
    messages: List[AIMessage],
    system_prompt: str,
    model: Model,
    attempt: int = 1,
    tools: AIToolSet | None = None,
    verbose: bool = True,
) -> LLMResponse:
    start_time = time.time()
    if verbose:
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

        data.execute_time = time.time() - start_time
        return data

    except APIException as e:
        if verbose:
            print(f"Error: {e.status_code}")
            print(f"Error: {e.content}")
        if e.status_code == 429:
            if verbose:
                print("Will try in 1 minute...")
            time.sleep(60)
            return ask_model(messages, system_prompt, model, attempt + 1, tools, verbose=verbose)
        else:
            if attempt > 2:
                return LLMResponse(
                    content=None, input_tokens=0, output_tokens=0,
                    error=f"### Error: {e.content}\n",
                )
            else:
                if verbose:
                    print("\tTrying again...")
                time.sleep(10)
                return ask_model(messages, system_prompt, model, attempt + 1, tools, verbose=verbose)
    except requests.exceptions.Timeout:
        if attempt > 2:
            return LLMResponse(
                content=None, input_tokens=0, output_tokens=0,
                error="### Error: Timeout error\n",
            )
        if verbose:
            print("\tRequest timed out. Trying again...")
        return ask_model(messages, system_prompt, model, attempt + 1, tools, verbose=verbose)
    except Exception as e:
        if verbose:
            print(f"\tError: {str(e)}")
        if attempt > 2:
            return LLMResponse(
                content=None, input_tokens=0, output_tokens=0,
                error="### Error: can not get the content\n",
            )
        else:
            if verbose:
                print("\tTrying again...")
            time.sleep(5)
            return ask_model(messages, system_prompt, model, attempt + 1, tools, verbose=verbose)
