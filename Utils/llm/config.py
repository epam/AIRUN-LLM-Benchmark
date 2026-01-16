import os
from dotenv import load_dotenv
from enum import Enum

from google.genai.types import ThinkingLevel
from openai.types import ReasoningEffort

load_dotenv()

deployed_llm_base_url = os.getenv("AZURE_DEPLOYMENT_BASE_URL")
deployed_llm_key = os.getenv("AZURE_DEPLOYMENT_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
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
        "api_key": openai_api_key,
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


def get_open_ai_responses_config(model, effort: ReasoningEffort = "high", verbosity=None, max_tokens=None, background=False):
    config = {
        "api_key": openai_api_key,
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
        **kwargs,
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


# thinking_level is supported only for Gemini 3 and above
def get_gemini_ai_studio_config(model, max_tokens=None, thinking_level: ThinkingLevel = None):
    return {"model_id": model, "max_tokens": max_tokens, "thinking_level": thinking_level}


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
    OPENAI_RESPONSES = "openai_responses"
    AZURE = "azure"
    FIREWORKS = "fireworks"
    XAI = "xai"
    AMAZON = "amazon"


class Model(Enum):
    # fmt: off
    # Gemini models
    Gemini_3_Pro_Preview = ("Gemini_3_Pro_Preview", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-3-pro-preview", max_tokens=65536, thinking_level=ThinkingLevel.HIGH))
    Gemini_3_Flash_Preview = ("Gemini_3_Flash_Preview", ModelProvider.AISTUDIO, lambda: get_gemini_ai_studio_config("gemini-3-flash-preview", max_tokens=65536, thinking_level=ThinkingLevel.HIGH))

    # OpenAI models
    GPT_OSS_120B = ("GPT_OSS_120B", ModelProvider.OPENAI, lambda: get_cerebras_config("gpt-oss-120b", max_tokens=32000, reasoning_effort="low"))
    GPT_OSS_20B = ("GPT_OSS_20B", ModelProvider.OPENAI, lambda: get_open_ai_config("openai/gpt-oss-20b", max_tokens=-1, reasoning_effort="low", base_url="http://localhost:1234/v1"))

    GPT5_Nano_high = ("GPT5_Nano_high", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5-nano-2025-08-07", effort="low", verbosity="high", max_tokens=128000))
    GPT5_Mini_high = ("GPT5_Mini_high", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5-mini-2025-08-07", effort="high", verbosity="high", max_tokens=128000))
    GPT51_Codex = ("GPT51_Codex", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5.1-codex", effort="high", max_tokens=128000))
    GPT51_Codex_mini = ("GPT51_Codex_mini", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5.1-codex-mini", effort="high", max_tokens=128000))
    GPT52_1211 = ("GPT52_1211", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5.2-2025-12-11", effort="none", verbosity="high", max_tokens=128000))
    GPT52_1211_high = ("GPT52_1211_high", ModelProvider.OPENAI_RESPONSES, lambda: get_open_ai_responses_config("gpt-5.2-2025-12-11", effort="high", verbosity="high", max_tokens=128000))

    # Claude models
    Sonnet_45 = ("Claude_Sonnet_45", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-sonnet-4-5@20250929"))
    Sonnet_45_high = ("Claude_Sonnet_45_high", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-sonnet-4-5@20250929", True))
    Opus_45 = ("Claude_Opus_45", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-opus-4-5@20251101"))
    Opus_45_high = ("Claude_Opus_45_high", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-opus-4-5@20251101", True))
    Haiku_45 = ("Claude_Haiku_45", ModelProvider.VERTEXAI_ANTHROPIC, lambda: get_anthropic_vertexai_config("claude-haiku-4-5@20251001"))

    # Other models
    Grok4_0709 = ("Grok4_0709", ModelProvider.XAI, lambda: get_xai_config("grok-4-0709")) # reasoning effort is not supported for Grok4
    Grok_Code_0825 = ("Grok_Code_0825", ModelProvider.XAI, lambda: get_xai_config("grok-code-fast-1-0825"))
    Grok41_Fast = ("Grok41_Fast", ModelProvider.XAI, lambda: get_xai_config("grok-4-1-fast-non-reasoning"))
    Grok41_FastReasoning = ("Grok41_FastReasoning", ModelProvider.XAI, lambda: get_xai_config("grok-4-1-fast-reasoning"))
    AmazonNovaPremier = ("AmazonNovaPremier", ModelProvider.AMAZON, lambda: get_amazon_nova_model_config("us.amazon.nova-premier-v1:0"))

    MiniMax_M21 = ("MiniMax_M21", ModelProvider.FIREWORKS, lambda: get_fireworks_config("accounts/fireworks/models/minimax-m2p1", max_tokens=16000))
    DeepSeek_v32 = ("DeepSeek_v32", ModelProvider.FIREWORKS, lambda: get_fireworks_config("accounts/fireworks/models/deepseek-v3p2", max_tokens=60000))
    Kimi_K2 = ("Kimi_K2", ModelProvider.FIREWORKS, lambda: get_fireworks_config("accounts/fireworks/models/kimi-k2-thinking", max_tokens=60000))
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
