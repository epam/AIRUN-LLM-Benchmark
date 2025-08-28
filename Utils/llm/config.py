import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

deployed_llm_base_url = os.getenv("AZURE_DEPLOYMENT_BASE_URL")
deployed_llm_key = os.getenv("AZURE_DEPLOYMENT_KEY")
open_api_key = os.getenv("OPENAI_API_KEY")
xai_api_key = os.getenv("XAI_API_KEY")
fireworks_api_key = os.getenv("FIREWORKS_API_KEY")
cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
google_ai_api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
gcloud_project_id = os.getenv("GCLOUD_PROJECT_ID")
default_temperature = 0
attempts_count = 1


def get_azure_config(model, max_tokens=None):
    def config():
        return {
            "max_tokens": max_tokens,
            "model_id": model,
            "api_key": deployed_llm_key,
            "url": f"{deployed_llm_base_url}/openai/deployments/{model}/chat/completions?api-version=2023-12-01-preview",
        }

    return config


def get_open_ai_config(
    model, max_tokens=None, skip_system=False, system_role_name="system", base_url="https://api.openai.com/v1", reasoning_effort=None
):
    config = {
        "model_id": model,
        "api_key": open_api_key,
        "max_tokens": max_tokens,
        "skip_system": skip_system,
        "system_role_name": system_role_name,
        "url": f"{base_url}",
        "reasoning_effort": reasoning_effort,
    }

    # if reasoning model o1, o3 or o4, change temperature and reasoning effort
    if model.startswith("o1") or model.startswith("o3") or model.startswith("o4"):
        config["temperature"] = 1
        config["reasoning_effort"] = "high"

    return config


def get_open_ai_responses_config(model, effort="high", verbosity=None, max_tokens=None):
    config = {
        "max_tokens": max_tokens,
        "model_id": model,
        "temperature": 1,
        "reasoning_effort": effort,
        "verbosity": verbosity,
    }

    return config


def get_xai_config(model, **kwargs):
    return {
        "model_id": model,
        "api_key": xai_api_key,
        "url": "https://api.x.ai/v1",
        "extra_params": kwargs,
    }


def get_fireworks_config(model, max_tokens):
    return {
        "model_id": model,
        "max_tokens": max_tokens,
        "api_key": fireworks_api_key,
        "url": "https://api.fireworks.ai/inference/v1",
    }


def get_cerebras_config(model, max_tokens, reasoning_effort):
    return {
        "model_id": model,
        "max_tokens": max_tokens,
        "api_key": cerebras_api_key,
        "reasoning_effort": reasoning_effort,
        "url": "https://api.cerebras.ai/v1",
    }


def get_gemini_ai_studio_config(model, max_tokens=None):
    return {"model_id": model, "max_tokens": max_tokens}


# Docs: https://docs.anthropic.com/en/api/claude-on-vertex-ai#making-requests
def get_anthropic_vertexai_config(model, enabled_thinking=False, max_tokens=None):
    thinking = {"type": "disabled"}

    if enabled_thinking:
        thinking = {
            "type": "enabled",
            "budget_tokens": 15000,
        }

    return {
        "region": "us-east5",
        "project_id": gcloud_project_id,
        "model_id": model,
        "thinking": thinking,
        "max_tokens": max_tokens or 64000,
        "temperature": 1 if enabled_thinking else default_temperature,
    }


def get_amazon_nova_model_config(model):
    MODEL_ID = model

    return {"model_id": MODEL_ID}


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
    # fmt: off
    # Gemini models
    Gemini_25_Pro_0506 = ("Gemini_25_Pro_0506", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-2.5-pro-preview-05-06", max_tokens=65536))
    Gemini_25_Pro_0605 = ("Gemini_25_Pro_0605", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-2.5-pro-preview-06-05", max_tokens=65536))
    Gemini_25_Flash_0520 = ("Gemini_25_Flash_0520", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-2.5-flash-preview-05-20", max_tokens=65536))

    # OpenAI models
    GPT35_Turbo_0125 = ("GPT35_Turbo_0125", ModelProvider.AZURE, lambda: get_azure_config("gpt-35-turbo-0125"))
    GPT4o_0513 = ("GPT4o_0513", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4o-2024-05-13"))
    GPT4o_0806 = ("GPT4o_0806", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4o-2024-08-06", 16384))
    GPT4o_1120 = ("GPT4o_1120", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4o-2024-11-20"))
    GPT45_0227 = ("GPT45_0227", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4.5-preview-2025-02-27", 16384))
    ChatGPT4o = ("ChatGPT4o", ModelProvider.OPENAI, lambda: get_open_ai_config("chatgpt-4o-latest", 16384))
    GPT4o_mini = ("GPT4o_mini", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4o-mini-2024-07-18"))
    OpenAi_o1_0912 = ("OpenAi_o1_0912", ModelProvider.OPENAI, lambda: get_open_ai_config("o1-preview-2024-09-12", skip_system=True))
    OpenAi_o1_1217 = ("OpenAi_o1_1217", ModelProvider.OPENAI, lambda: get_open_ai_config("o1-2024-12-17", system_role_name="developer"))
    OpenAi_o1_mini_0912 = ("OpenAi_o1_mini_0912", ModelProvider.OPENAI, lambda: get_open_ai_config("o1-mini-2024-09-12", skip_system=True))
    OpenAi_o3_mini_0131 = ("OpenAi_o3_mini_0131", ModelProvider.OPENAI, lambda: get_open_ai_config("o3-mini-2025-01-31", system_role_name="developer"))
    GPT41_0414 = ("GPT41_0414", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4.1-2025-04-14", system_role_name="developer"))
    GPT41mini_0414 = ("GPT41mini_0414", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4.1-mini-2025-04-14", system_role_name="developer"))
    GPT41nano_0414 = ("GPT41nano_0414", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4.1-nano-2025-04-14"))
    OpenAi_o3_0416 = ("OpenAi_o3_0416", ModelProvider.OPENAI, lambda: get_open_ai_config("o3-2025-04-16", system_role_name="developer"))
    OpenAi_o4_mini_0416 = ("OpenAi_o4_mini_0416", ModelProvider.OPENAI, lambda: get_open_ai_config("o4-mini-2025-04-16", system_role_name="developer"))
    Gemma_3_1B = ("Gemma_3_1B", ModelProvider.OPENAI, lambda: get_open_ai_config("google/gemma-3-1b-it", base_url="http://10.82.37.83:8000/v1"))
    Gemma_3_4B = ("Gemma_3_4B", ModelProvider.OPENAI, lambda: get_open_ai_config("google/gemma-3-4b-it", base_url="http://10.82.37.84:8000/v1"))
    Gemma_3_27B = ("Gemma_3_27B", ModelProvider.OPENAI, lambda: get_open_ai_config("google/gemma-3-27b-it-qat-q4_0-gguf", base_url="http://10.82.37.86:8000/v1"))
    Gemma_3_12B = ("Gemma_3_12B", ModelProvider.OPENAI, lambda: get_open_ai_config("google/gemma-3-12b-it-qat-q4_0-gguf", base_url="http://10.82.37.86:8000/v1"))
    GPT_OSS_120B = ("GPT_OSS_120B", ModelProvider.OPENAI, lambda: get_cerebras_config("gpt-oss-120b", max_tokens=65536, reasoning_effort="low"))
    GPT_OSS_20B = ("GPT_OSS_20B", ModelProvider.OPENAI, lambda: get_open_ai_config("openai/gpt-oss-20b", max_tokens=-1, reasoning_effort="low", base_url="http://localhost:1234/v1"))

    OpenAi_o1_pro_0319 = ("OpenAi_o1_pro_0319", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("o1-pro-2025-03-19"))
    OpenAi_o3_pro_0610 = ("OpenAi_o3_pro_0610", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("o3-pro-2025-06-10", max_tokens=100000))
    Codex_Mini_Latest = ("Codex_Mini_Latest", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("codex-mini-latest", max_tokens=100000))
    GPT5_0807 = ("GPT5_0807", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5", effort="low", verbosity="high", max_tokens=128000))

    # Claude models
    Sonnet_4 = ("Claude_Sonnet_4", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-sonnet-4@20250514"))
    Sonnet_4_Thinking = ("Claude_Sonnet_4_Thinking", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-sonnet-4@20250514", True))
    Opus_4_Thinking = ("Claude_Opus_4_Thinking", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-opus-4@20250514", True, 32000))
    Opus_41 = ("Claude_Opus_41", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-opus-4-1@20250805", False, 32000))

    # Other models
    GrokBeta = ("GrokBeta", ModelProvider.XAI, lambda: get_xai_config("grok-beta"))
    Grok2_1212 = ("Grok2_1212", ModelProvider.XAI, lambda: get_xai_config("grok-2-1212"))
    Grok3_beta = ("Grok3_beta", ModelProvider.XAI, lambda: get_xai_config("grok-3"))
    Grok3mini_beta = ("Grok3mini_beta", ModelProvider.XAI, lambda: get_xai_config("grok-3-mini", reasoning_effort="high"))
    Grok4_0709 = ("Grok4_0709", ModelProvider.XAI, lambda: get_xai_config("grok-4-0709")) # reasoning effort is not supported for Grok4
    Qwen25Coder32B = ("Qwen25Coder32B", ModelProvider.FIREWORKS, lambda: get_fireworks_config("accounts/fireworks/models/qwen2p5-coder-32b-instruct", 4096))
    DeepSeekR1 = ("DeepSeekR1", ModelProvider.FIREWORKS, lambda: get_fireworks_config("accounts/fireworks/models/deepseek-r1", 16000))
    DeepSeekV3_0324 = ("DeepSeekV3_0324", ModelProvider.FIREWORKS, lambda: get_fireworks_config("accounts/fireworks/models/deepseek-v3-0324", 16000))
    DeepSeekR1_0528 = ("DeepSeekR1_0528", ModelProvider.FIREWORKS, lambda: get_fireworks_config("accounts/fireworks/models/deepseek-r1-0528", 16000))
    Llama_4_Maverick = ("Llama_4_Maverick", ModelProvider.FIREWORKS, lambda: get_fireworks_config("accounts/fireworks/models/llama4-maverick-instruct-basic", 131000))
    AmazonNovaPro = ("AmazonNovaPro", ModelProvider.AMAZON, lambda: get_amazon_nova_model_config("us.amazon.nova-pro-v1:0"))
    AmazonNovaPremier = ("AmazonNovaPremier", ModelProvider.AMAZON, lambda: get_amazon_nova_model_config("us.amazon.nova-premier-v1:0"))
    # fmt: on

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
