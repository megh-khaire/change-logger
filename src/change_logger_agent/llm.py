import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def generate_llm_response(
    input: list[dict], output_model: BaseModel, model: str = "gpt-4.1"
) -> str:
    response = client.responses.parse(
        model=model,
        input=input,
        text_format=output_model
    )
    return response.output_parsed
