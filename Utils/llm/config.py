import os
import subprocess
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

deployed_llm_base_url = os.getenv('AZURE_DEPLOYMENT_BASE_URL')
deployed_llm_key = os.getenv('AZURE_DEPLOYMENT_KEY')
open_api_key = os.getenv('OPENAI_API_KEY')
xai_api_key = os.getenv('XAI_API_KEY')
fireworks_api_key = os.getenv('FIREWORKS_API_KEY')
google_ai_api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
gcloud_path = os.getenv('GCLOUD_PATH')
gcloud_project_id = os.getenv('GCLOUD_PROJECT_ID')
default_temperature = 0
attempts_count = 1


def get_gcp_access_token():
    return subprocess.check_output(
        [gcloud_path, 'auth', 'print-access-token']).decode('utf-8').strip()


def get_azure_config(model, max_tokens=None):
    def config():
        return {
            "max_tokens": max_tokens,
            "model_id": model,
            "api_key": deployed_llm_key,
            "url": f'{deployed_llm_base_url}/openai/deployments/{model}/chat/completions?api-version=2023-12-01-preview'
        }

    return config


def get_open_ai_config(model, max_tokens=None, skip_system=False, system_role_name="system"):
    config = {
        "model_id": model,
        "api_key": open_api_key,
        "max_tokens": max_tokens,
        "skip_system": skip_system,
        "system_role_name": system_role_name,
        "url": 'https://api.openai.com/v1/chat/completions'
    }

    # if reasoning model o1 or o3, change temperature
    if model.startswith("o1") or model.startswith("o3"):
        config["temperature"] = 1

    return config

def get_open_ai_responses_config(model):
    config = {
        "model_id": model,
        "api_key": open_api_key,
        "url": 'https://api.openai.com/v1/responses'
    }

    if model.startswith("o1") or model.startswith("o3"):
        config["temperature"] = 1
        config["reasoning_effort"] = "medium"

    return config


def get_xai_config(model):
    return {
        "model_id": model,
        "api_key": xai_api_key,
        "url": 'https://api.x.ai/v1/chat/completions'
    }


def get_fireworks_config(model, max_tokens):
    return {
        "model_id": model,
        "max_tokens": max_tokens,
        "api_key": fireworks_api_key,
        "url": "https://api.fireworks.ai/inference/v1/chat/completions"
    }


def get_gemini_ai_studio_config(model, skip_system=False, max_tokens=None):
    return {
        "model_id": model,
        "skip_system": skip_system,
        "max_tokens": max_tokens,
        "url": f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={google_ai_api_key}"
    }


def get_anthropic_vertexai_config(model, location_id=None):
    LOCATION_ID = location_id or "europe-west1"
    PROJECT_ID = gcloud_project_id
    gcp_access_token = get_gcp_access_token()

    return {
        "version": "vertex-2023-10-16",
        "model_id": model,
        "api_key": gcp_access_token,
        "url": f"https://{LOCATION_ID}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/anthropic/models/{model}:streamRawPredict"
    }


def get_amazon_nova_pro_config():
    MODEL_ID = "us.amazon.nova-pro-v1:0"

    return {
        "model_id": MODEL_ID
    }


def get_sonnet_37_vertex_config(enabled_thinking=False):
    LOCATION_ID = "us-east5"
    PROJECT_ID = gcloud_project_id
    MODEL_ID = "claude-3-7-sonnet@20250219"
    gcp_access_token = get_gcp_access_token()

    thinking = {
        "type": "disabled"
    }

    if enabled_thinking:
        thinking = {
            "type": "enabled",
            "budget_tokens": 4096,
        }

    return {
        "version": "vertex-2023-10-16",
        "model_id": MODEL_ID,
        "api_key": gcp_access_token,
        "extra_params": {
            "thinking": thinking,
            "max_tokens": 20000 if enabled_thinking else 8192,
            "temperature": 1 if enabled_thinking else default_temperature
        },
        "url": f"https://{LOCATION_ID}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/anthropic/models/{MODEL_ID}:streamRawPredict"
    }


class ModelProvider(Enum):
    AISTUDIO = "aistudio"
    VERTEXAI = "vertexai"
    VERTEXAI_ANTHROPIC = "vertexai_anthropic"
    OPENAI = "openai"
    OPENAI_RESPONSES = "OPENAI_RESPONSES"
    AZURE = "azure"
    FIREWORKS = "fireworks"
    XAI = "xai"
    AMAZON = "amazon"


class Model(Enum):
    # Gemini models
    Gemini_15_Pro_002 = ("Gemini_15_Pro_002", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-1.5-pro-002"))
    Gemini_20_Flash_Think_0121 = ("Gemini_20_Flash_Think_0121", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-2.0-flash-thinking-exp-01-21"))
    Gemini_20_Pro_0205 = ("Gemini_20_Pro_0205", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-2.0-pro-exp-02-05"))
    Gemma_3_27B = ("Gemma_3_27B", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemma-3-27b-it", True))
    Gemini_25_Pro_0325 = ("Gemini_25_Pro_0325", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-2.5-pro-exp-03-25", max_tokens=65000))

    # OpenAI models
    GPT35_Turbo_0125 = ("GPT35_Turbo_0125", ModelProvider.AZURE, lambda: get_azure_config('gpt-35-turbo-0125'))
    GPT4o_0513 = ("GPT4o_0513", ModelProvider.OPENAI, lambda: get_open_ai_config('gpt-4o-2024-05-13'))
    GPT4o_0806 = ("GPT4o_0806", ModelProvider.OPENAI, lambda: get_open_ai_config('gpt-4o-2024-08-06', 16384))
    GPT4o_1120 = ("GPT4o_1120", ModelProvider.OPENAI, lambda: get_open_ai_config('gpt-4o-2024-11-20'))
    GPT45_0227 = ("GPT45_0227", ModelProvider.OPENAI, lambda: get_open_ai_config('gpt-4.5-preview-2025-02-27', 16384))
    ChatGPT4o = ("ChatGPT4o", ModelProvider.OPENAI, lambda: get_open_ai_config('chatgpt-4o-latest', 16384))
    GPT4o_mini = ("GPT4o_mini", ModelProvider.OPENAI, lambda: get_open_ai_config('gpt-4o-mini-2024-07-18'))
    OpenAi_o1_0912 = ("OpenAi_o1_0912", ModelProvider.OPENAI, lambda: get_open_ai_config('o1-preview-2024-09-12', skip_system=True))
    OpenAi_o1_1217 = ("OpenAi_o1_1217", ModelProvider.OPENAI, lambda: get_open_ai_config('o1-2024-12-17', system_role_name="developer"))
    OpenAi_o1_mini_0912 = ("OpenAi_o1_mini_0912", ModelProvider.OPENAI, lambda: get_open_ai_config('o1-mini-2024-09-12', skip_system=True))
    OpenAi_o3_mini_0131 = ("OpenAi_o3_mini_0131", ModelProvider.OPENAI, lambda: get_open_ai_config('o3-mini-2025-01-31', system_role_name="developer"))

    OpenAi_o1_pro_0319 = ("OpenAi_o1_pro_0319", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config('o1-pro-2025-03-19'))
    # Claude models
    Haiku_35 = ("Claude_Haiku_35", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config('claude-3-5-haiku@20241022', 'us-east5'))
    Sonnet_35 = ("Claude_Sonnet_35", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config('claude-3-5-sonnet@20240620'))
    Sonnet_35v2 = ("Claude_Sonnet_35v2", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config('claude-3-5-sonnet-v2@20241022'))
    Sonnet_37 = ("Claude_Sonnet_37", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_sonnet_37_vertex_config())
    Sonnet_37_Thinking = ("Claude_Sonnet_37_Thinking", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_sonnet_37_vertex_config(True))

    # Other models
    GrokBeta = ("GrokBeta", ModelProvider.XAI, lambda: get_xai_config('grok-beta'))
    Grok2_1212 = ("Grok2_1212", ModelProvider.XAI, lambda: get_xai_config('grok-2-1212'))
    Qwen25Coder32B = ("Qwen25Coder32B", ModelProvider.FIREWORKS, lambda: get_fireworks_config('accounts/fireworks/models/qwen2p5-coder-32b-instruct', 4096))
    DeepSeekR1 = ("DeepSeekR1", ModelProvider.FIREWORKS, lambda: get_fireworks_config('accounts/fireworks/models/deepseek-r1', 16000))
    DeepSeekV3_0324 = ("DeepSeekV3_0324", ModelProvider.FIREWORKS, lambda: get_fireworks_config('accounts/fireworks/models/deepseek-v3-0324', 16000))
    Llama_4_Maverick = ("Llama_4_Maverick", ModelProvider.FIREWORKS, lambda: get_fireworks_config('accounts/fireworks/models/llama4-maverick-instruct-basic', 131000))
    AmazonNovaPro = ("AmazonNovaPro", ModelProvider.AMAZON, lambda: get_amazon_nova_pro_config())

    def __init__(self, model_id: str, provider: ModelProvider, config_func: callable):
        """Initialize the model"""
        self.model_id = model_id
        self.provider = provider
        self.config_func = config_func

    def __call__(self):
        """Get the configuration for this model"""
        return self.config_func()

    def __str__(self):
        """Return the model ID"""
        return self.model_id
