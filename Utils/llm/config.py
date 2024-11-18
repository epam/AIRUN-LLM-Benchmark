import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

deployed_llm_base_url = os.getenv('LLM_PROVIDER_BASE_URL')
deployed_llm_key = os.getenv('LLM_PROVIDER_KEY')
open_api_key = os.getenv('OPENAI_API_KEY')
xai_api_key = os.getenv('XAI_API_KEY')
fireworks_api_key = os.getenv('FIREWORKS_API_KEY')
google_ai_api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
gcloud_path = os.getenv('GCLOUD_PATH')
gcloud_project_id = os.getenv('GCLOUD_PROJECT_ID')
temperature = 0
attempts_count = 1


def get_gcp_access_token():
    return subprocess.check_output(
        [gcloud_path, 'auth', 'print-access-token']).decode('utf-8').strip()


class Model:
    Gemini = "Gemini1_0"
    GPT4 = "GPT4_Turbo"
    GeminiPro = "Gemini1_5"
    GeminiPro_0801 = "GeminiPro_0801"
    Gemini_15_Pro_002 = "Gemini_15_Pro_002"
    GeminiPro_1114 = "GeminiPro_1114"
    GeminiPro_1121 = "GeminiPro_1121"
    Opus_3 = "Claude_Opus_3"
    Sonnet_35 = "Claude_Sonnet_35"
    Sonnet_35v2 = "Claude_Sonnet_35v2"
    Haiku_35 = "Claude_Haiku_35"
    GPT35_Turbo_0125 = "GPT35_Turbo_0125"
    GPT4_Turbo_0409 = "GPT4_Turbo_0409"
    GPT4o_0513 = "GPT4o_0513"
    GPT4o_0806 = "GPT4o_0806"
    GPT4o_1120 = "GPT4o_1120"
    ChatGPT4o = "ChatGPT4o"
    GPT4o_mini = "GPT4o_mini_0718"
    OpenAi_o1_0912 = "OpenAi_o1_0912"
    OpenAi_o1_mini_0912 = "OpenAi_o1_mini_0912"
    Llama3_70B = "Llama3_70B"
    Llama31_405B = "Llama31_405B"
    GrokBeta = "GrokBeta"
    Qwen25Coder32B = "Qwen25Coder32B"


def get_azure_config(model):
    def config():
        return {
            "model_id": model,
            "api_key": deployed_llm_key,
            "url": f'{deployed_llm_base_url}/openai/deployments/{model}/chat/completions?api-version=2023-12-01-preview'
        }

    return config


def get_open_ai_config(model, max_tokens=None, skip_system=False):
    def config():
        return {
            "model_id": model,
            "api_key": open_api_key,
            "max_tokens": max_tokens,
            "skip_system": skip_system,
            "url": 'https://api.openai.com/v1/chat/completions'
        }

    return config


def get_xai_config(model):
    def config():
        return {
            "model_id": model,
            "api_key": xai_api_key,
            "url": 'https://api.x.ai/v1/chat/completions'
        }

    return config


def get_fireworks_config(model, max_tokens):
    def config():
        return {
            "model_id": model,
            "max_tokens": max_tokens,
            "api_key": fireworks_api_key,
            "url": "https://api.fireworks.ai/inference/v1/chat/completions"
        }

    return config


def get_gemini_pro_config():
    gcp_access_token = get_gcp_access_token()
    LOCATION_ID = "us-central1"
    PROJECT_ID = gcloud_project_id
    MODEL_ID = "gemini-1.5-pro-preview-0409"

    return {
        "model_id": MODEL_ID,
        "api_key": gcp_access_token,
        "url": f"https://{LOCATION_ID}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/google/models/{MODEL_ID}:generateContent"
    }


def get_gemini_ai_studio_config(model):
    def config():
        return {
            "model_id": model,
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={google_ai_api_key}"
        }

    return config


def get_opus_3_config():
    gcp_access_token = get_gcp_access_token()
    LOCATION_ID = "us-east5"
    PROJECT_ID = gcloud_project_id
    MODEL_ID = "claude-3-opus@20240229"

    return {
        "version": "vertex-2023-10-16",
        "model_id": MODEL_ID,
        "api_key": gcp_access_token,
        "url": f"https://{LOCATION_ID}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/anthropic/models/{MODEL_ID}:streamRawPredict"
    }


def get_sonnet_35_config():
    gcp_access_token = get_gcp_access_token()
    LOCATION_ID = "europe-west1"
    PROJECT_ID = gcloud_project_id
    MODEL_ID = "claude-3-5-sonnet@20240620"

    return {
        "version": "vertex-2023-10-16",
        "model_id": MODEL_ID,
        "api_key": gcp_access_token,
        "url": f"https://{LOCATION_ID}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/anthropic/models/{MODEL_ID}:streamRawPredict"
    }


def get_sonnet_35_v2_config():
    gcp_access_token = get_gcp_access_token()
    # LOCATION_ID = "us-east5"
    LOCATION_ID = "europe-west1"
    PROJECT_ID = gcloud_project_id
    MODEL_ID = "claude-3-5-sonnet-v2@20241022"

    return {
        "version": "vertex-2023-10-16",
        "model_id": MODEL_ID,
        "api_key": gcp_access_token,
        "url": f"https://{LOCATION_ID}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/anthropic/models/{MODEL_ID}:streamRawPredict"
    }


def get_haiku_35_config():
    gcp_access_token = get_gcp_access_token()
    LOCATION_ID = "us-east5"
    PROJECT_ID = gcloud_project_id
    MODEL_ID = "claude-3-5-haiku@20241022"

    return {
        "version": "vertex-2023-10-16",
        "model_id": MODEL_ID,
        "api_key": gcp_access_token,
        "url": f"https://{LOCATION_ID}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/anthropic/models/{MODEL_ID}:streamRawPredict"
    }


API = {
    Model.Gemini: get_azure_config('gemini-pro'),
    Model.GeminiPro: get_gemini_pro_config,
    Model.GeminiPro_0801: get_gemini_ai_studio_config('gemini-1.5-pro-exp-0801'),
    Model.Gemini_15_Pro_002: get_gemini_ai_studio_config("gemini-1.5-pro-002"),
    Model.GeminiPro_1114: get_gemini_ai_studio_config("gemini-exp-1114"),
    Model.GeminiPro_1121: get_gemini_ai_studio_config("gemini-exp-1121"),
    Model.GPT4: get_azure_config('gpt-4-0125-preview'),
    Model.GPT35_Turbo_0125: get_azure_config('gpt-35-turbo-0125'),
    Model.GPT4_Turbo_0409: get_open_ai_config('gpt-4-turbo-2024-04-09'),
    Model.GPT4o_0513: get_open_ai_config('gpt-4o-2024-05-13'),
    Model.GPT4o_0806: get_open_ai_config('gpt-4o-2024-08-06', 16384),
    Model.GPT4o_1120: get_open_ai_config('gpt-4o-2024-11-20'),
    Model.ChatGPT4o: get_open_ai_config('chatgpt-4o-latest', 16384),
    Model.GPT4o_mini: get_open_ai_config('gpt-4o-mini-2024-07-18'),
    Model.OpenAi_o1_0912: get_open_ai_config('o1-preview-2024-09-12', skip_system=True),
    Model.OpenAi_o1_mini_0912: get_open_ai_config('o1-mini-2024-09-12', skip_system=True),
    Model.Opus_3: get_opus_3_config,
    Model.Sonnet_35: get_sonnet_35_config,
    Model.Sonnet_35v2: get_sonnet_35_v2_config,
    Model.Haiku_35: get_haiku_35_config,
    Model.Llama3_70B: get_azure_config('llama-3-70b-instruct-awq'),
    Model.Llama31_405B: get_fireworks_config("accounts/fireworks/models/llama-v3p1-405b-instruct", 16384),
    Model.GrokBeta: get_xai_config('grok-beta'),
    Model.Qwen25Coder32B: get_fireworks_config("accounts/fireworks/models/qwen2p5-coder-32b-instruct", 4096),
}