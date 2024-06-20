import os

import instructor
from pydantic import BaseModel

from anthropic import Anthropic
import openai

from core.types import ModelConfig


def llm_response(config: ModelConfig, response_model: BaseModel, system: str, message: str):
    provider = config.provider
    if provider == "anthropic":
        client = instructor.from_anthropic(Anthropic(), mode=instructor.Mode.ANTHROPIC_TOOLS)
        return client.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            messages=[
                {"role": "system",
                 "content": system
                 },
                {
                    "role": "user",
                    "content": message
                }
            ],
            response_model=response_model)
    elif provider == "together":
        client = openai.OpenAI(
            base_url="https://api.together.xyz/v1",
            api_key=os.environ["TOGETHER_API_KEY"])
        client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)
        return client.messages.create(
            model="meta-llama/Meta-Llama-3-70B",
            max_tokens=4096,
            messages=[
                {"role": "system",
                 "content": system
                 },
                {
                    "role": "user",
                    "content": message
                }
            ],
            response_model=response_model)
    elif provider == "groq":
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        client = instructor.from_openai(client, mode=instructor.Mode.MD_JSON)
        return client.messages.create(
            model="meta-llama/Meta-Llama-3-70B",
            max_tokens=4096,
            messages=[
                {"role": "system",
                 "content": system
                 },
                {
                    "role": "user",
                    "content": message
                }
            ],
            response_model=response_model)