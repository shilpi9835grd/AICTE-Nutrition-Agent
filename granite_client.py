"""
AICTE Nutrition Agent — IBM Granite watsonx.ai Client
Handles authentication and text generation via IBM watsonx.ai chat API.

SDK version: ibm-watsonx-ai 1.9.0
All models available on this deployment are chat models (e.g. ibm/granite-4-h-small).
They support the /ml/v1/text/chat endpoint accessed via ModelInference.chat().
They do NOT support the /ml/v1/text/generation endpoint (generate_text()), which
is for base/instruct-generation-only models — calling it raises:
    model_no_support_for_function
"""

import os
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters
from dotenv import load_dotenv

load_dotenv()


def _get_credentials() -> Credentials:
    return Credentials(
        url=os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        api_key=os.getenv("IBM_API_KEY"),
    )


def get_model() -> ModelInference:
    """Return a configured IBM Granite ModelInference instance."""
    creds = _get_credentials()
    project_id = os.getenv("IBM_PROJECT_ID")
    # Default to ibm/granite-4-h-small — the IBM-native chat model available
    # on this deployment. Override via GRANITE_MODEL_ID in .env.
    model_id = os.getenv("GRANITE_MODEL_ID", "ibm/granite-4-h-small")

    model = ModelInference(
        model_id=model_id,
        credentials=creds,
        project_id=project_id,
    )
    return model


def generate(prompt: str, max_tokens: int = 1024, system: str = "") -> str:
    """
    Send a prompt to IBM Granite via the chat API and return the generated text.

    Args:
        prompt:     The user-turn content (task instruction + context).
        max_tokens: Maximum tokens to generate.
        system:     Optional system message (persona/instructions). When provided
                    it is sent as the 'system' role message before the user turn.

    Uses ModelInference.chat() which maps to POST /ml/v1/text/chat — the correct
    endpoint for all chat models (granite-4, llama-3, mistral, etc.).
    """
    model = get_model()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    params = TextChatParameters(
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.1,
    )

    response = model.chat(messages=messages, params=params)

    # chat() returns a dict with OpenAI-compatible structure:
    # {"choices": [{"message": {"role": "assistant", "content": "..."}}], ...}
    try:
        content = response["choices"][0]["message"]["content"]
        return content.strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected response structure from IBM Granite chat(): {response}") from e
