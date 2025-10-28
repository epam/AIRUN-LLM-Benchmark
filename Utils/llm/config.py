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
    model,
    max_tokens=None,
    skip_system=False,
    system_role_name="system",
    base_url="https://api.openai.com/v1",
    reasoning_effort=None,
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


def get_open_ai_responses_config(model, effort="high", verbosity=None, max_tokens=None, background=False):
    config = {
        "max_tokens": max_tokens,
        "model_id": model,
        "temperature": 1,
        "reasoning_effort": effort,
        "verbosity": verbosity,
        "background": background,
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
            "budget_tokens": 2048,
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
    OPENAI_RESPONSES = "openai_responses"
    AZURE = "azure"
    FIREWORKS = "fireworks"
    XAI = "xai"
    AMAZON = "amazon"


class Model(Enum):
    # fmt: off
    # Gemini models
    Gemini_25_Pro = ("Gemini_25_Pro", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-2.5-pro", max_tokens=65536))
    Gemini_25_Flash = ("Gemini_25_Flash", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-2.5-flash", max_tokens=65536))
    Gemini_25_Flash_0925 = ("Gemini_25_Flash_0925", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-2.5-flash-preview-09-2025", max_tokens=65536))

    # OpenAI models
    GPT41_0414 = ("GPT41_0414", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4.1-2025-04-14", system_role_name="developer"))
    GPT41mini_0414 = ("GPT41mini_0414", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4.1-mini-2025-04-14", system_role_name="developer"))
    GPT41nano_0414 = ("GPT41nano_0414", ModelProvider.OPENAI, lambda: get_open_ai_config("gpt-4.1-nano-2025-04-14"))
    GPT_OSS_120B = ("GPT_OSS_120B", ModelProvider.OPENAI, lambda: get_cerebras_config("gpt-oss-120b", max_tokens=65536, reasoning_effort="low"))
    GPT_OSS_20B = ("GPT_OSS_20B", ModelProvider.OPENAI, lambda: get_open_ai_config("openai/gpt-oss-20b", max_tokens=-1, reasoning_effort="low", base_url="http://localhost:1234/v1"))

    Codex_Mini_Latest = ("Codex_Mini_Latest", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("codex-mini-latest", max_tokens=100000))
    GPT5_0807 = ("GPT5_0807", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5-2025-08-07", effort="low", verbosity="high", max_tokens=128000))
    GPT5_Pro_1006 = ("GPT5_Pro_1006", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5-pro-2025-10-06", verbosity="high", max_tokens=272000, background=True))
    GPT5_Codex = ("GPT5_Codex", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5-codex", effort="low", verbosity="medium", max_tokens=128000))
    GPT5_Nano_high = ("GPT5_Nano_high", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5-nano-2025-08-07", effort="high", verbosity="high", max_tokens=128000))
    GPT5_Mini_high = ("GPT5_Mini_high", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5-mini-2025-08-07", effort="high", verbosity="high", max_tokens=128000))

    # Claude models
    Sonnet_4 = ("Claude_Sonnet_4", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-sonnet-4@20250514"))
    Sonnet_4_Thinking = ("Claude_Sonnet_4_Thinking", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-sonnet-4@20250514", True))
    Sonnet_45 = ("Claude_Sonnet_45", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-sonnet-4-5@20250929"))
    Opus_41 = ("Claude_Opus_41", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-opus-4-1@20250805", False, 32000))
    Opus_41_Thinking = ("Claude_Opus_41_Thinking", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-opus-4-1@20250805", True, 32000))
    Haiku_45 = ("Claude_Haiku_45", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-haiku-4-5@20251001"))

    # Other models
    Grok4_0709 = ("Grok4_0709", ModelProvider.XAI, lambda: get_xai_config("grok-4-0709")) # reasoning effort is not supported for Grok4
    Grok_Code_0825 = ("Grok_Code_0825", ModelProvider.XAI, lambda: get_xai_config("grok-code-fast-1-0825"))
    Grok4FastReasoning = ("Grok4FastReasoning", ModelProvider.XAI, lambda: get_xai_config("grok-4-fast-reasoning-latest"))
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
